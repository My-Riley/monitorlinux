import ipaddress
import json
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Dict, List, Optional, Union

import jwt
from fastapi import Depends, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from user_agents import parse as parse_user_agent

from config.constant import CommonConstant, MenuConstant
from config.enums import RedisInitKeyConfig
from config.env import AppConfig, JwtConfig
from config.get_db import get_db
from exceptions.exception import AuthException, LoginException
from module_admin.dao.login_dao import login_by_account
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.log_do import SysLogininfor
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.vo.login_vo import MenuTreeModel, MetaModel, RouterModel, UserLogin
from module_admin.entity.vo.user_vo import CurrentUserModel, TokenData, UserInfoModel
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.pwd_util import PwdUtil

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class CustomOAuth2PasswordRequestForm(OAuth2PasswordRequestForm):
    """自定义OAuth2PasswordRequestForm类"""

    def __init__(
        self,
        grant_type: str = Form(default=None, regex="password"),
        username: str = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
        code: Optional[str] = Form(default=""),
        uuid: Optional[str] = Form(default=""),
        login_info: Optional[Dict[str, str]] = Form(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.code = code
        self.uuid = uuid
        self.login_info = login_info


class LoginService:
    """登录模块服务层"""

    @classmethod
    def _get_client_ip(cls, request: Request) -> str:
        """尽量获取真实客户端IP（兼容反向代理）"""
        xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
        if xff:
            # XFF: client, proxy1, proxy2
            return xff.split(",")[0].strip()
        xri = request.headers.get("x-real-ip") or request.headers.get("X-Real-IP")
        if xri:
            return xri.strip()
        return getattr(getattr(request, "client", None), "host", "") or ""

    @classmethod
    def _get_ua_info(cls, request: Request) -> tuple[str, str]:
        """解析 User-Agent，返回 (browser, os)"""
        ua_str = request.headers.get("user-agent") or request.headers.get("User-Agent") or ""
        if not ua_str:
            return "", ""
        ua = parse_user_agent(ua_str)
        browser = ua.browser.family or ""
        os_name = ua.os.family or ""
        # 附带主版本号，便于排查
        if ua.browser.version_string:
            browser = f"{browser} {ua.browser.version_string}"
        if ua.os.version_string:
            os_name = f"{os_name} {ua.os.version_string}"
        return browser, os_name

    @classmethod
    def _is_private_ip(cls, ip: str) -> bool:
        """判断是否为内网/保留地址（含 localhost）"""
        try:
            addr = ipaddress.ip_address(ip)
            return addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local or addr.is_multicast
        except Exception:
            return False

    @staticmethod
    @lru_cache(maxsize=2048)
    def _resolve_login_location_sync(ip: str) -> str:
        """解析登录地点（同步，带缓存）

        参考若依常用方案：公网IP调用第三方归属地查询，失败则降级为空。
        这里使用 `whois.pconline.com.cn` 的 JSON 接口（无需额外依赖）。
        """
        if not ip:
            return ""
        if ip in ("127.0.0.1", "::1"):
            return "本机"
        try:
            addr = ipaddress.ip_address(ip)
            if addr.is_private or addr.is_loopback or addr.is_reserved or addr.is_link_local or addr.is_multicast:
                return "内网IP"
        except Exception:
            # 非法IP直接返回空
            return ""

        # pconline：返回 GBK 编码 JSON，字段常见：pro/city/addr
        # 示例：`http://whois.pconline.com.cn/ipJson.jsp?ip=8.8.8.8&json=true`
        url = "http://whois.pconline.com.cn/ipJson.jsp?" + urllib.parse.urlencode({"ip": ip, "json": "true"})
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0",
                },
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                raw = resp.read()
            # 尝试 GBK -> UTF-8
            text = raw.decode("gbk", errors="ignore") if raw else ""
            data = json.loads(text) if text else {}
            pro = (data.get("pro") or "").strip()
            city = (data.get("city") or "").strip()
            addr = (data.get("addr") or "").strip()
            location = "".join([pro, city]).strip()
            # addr 有时包含更完整的描述（含运营商），可作为补充
            if addr and addr not in location:
                location = f"{location} {addr}".strip() if location else addr
            return location
        except Exception as e:
            # 失败不抛出，降级为空（不影响登录）
            logger.warning(f"解析登录地点失败(ip={ip}): {e}")
            return ""

    @classmethod
    async def record_logininfor(
        cls,
        *,
        request: Request,
        query_db: AsyncSession,
        user_name: str,
        status: str,
        msg: str,
        login_location: str = "",
    ) -> None:
        """记录登录日志（不应影响主流程）

        status: '0' 成功, '1' 失败（与 sys_logininfor 表定义一致）
        """
        try:
            ipaddr = cls._get_client_ip(request)
            browser, os_name = cls._get_ua_info(request)
            # 参考 RuoYi-Vue3-FastAPI：由 app_ip_location_query 控制是否查询归属地
            if (not login_location) and getattr(AppConfig, "app_ip_location_query", False):
                login_location = cls._resolve_login_location_sync(ipaddr)
            row = SysLogininfor(
                user_name=user_name,
                ipaddr=ipaddr,
                login_location=login_location or "",
                browser=browser,
                os=os_name,
                status=status,
                msg=msg or "",
                login_time=datetime.now(),
            )
            query_db.add(row)
            await query_db.commit()
        except Exception as e:
            # 记录失败不阻断登录流程
            try:
                await query_db.rollback()
            except Exception:
                pass
            logger.error(f"记录登录日志失败: {e}")

    @classmethod
    async def validate_captcha(cls, request: Request, code: str, captcha_uuid: str):
        """验证码校验"""
        # 检查验证码是否为空
        if not code or not code.strip():
            logger.warning("验证码不能为空")
            raise LoginException(data="", message="验证码不能为空")

        # 检查uuid是否为空
        if not captcha_uuid or not captcha_uuid.strip():
            logger.warning("验证码已过期，请刷新重试")
            raise LoginException(data="", message="验证码已过期，请刷新重试")

        # 从Redis获取验证码
        redis_key = f"{RedisInitKeyConfig.CAPTCHA_CODES.key}:{captcha_uuid}"
        stored_code = await request.app.state.redis.get(redis_key)

        # 验证码已过期或不存在
        if not stored_code:
            logger.warning("验证码已过期，请刷新重试")
            raise LoginException(data="", message="验证码已过期，请刷新重试")

        # 验证码校验（忽略大小写）
        if code.lower() != stored_code.lower():
            # 删除已使用的验证码，防止暴力破解
            await request.app.state.redis.delete(redis_key)
            logger.warning("验证码错误")
            raise LoginException(data="", message="验证码错误，请重新输入")

        # 验证成功后删除验证码，防止重复使用
        await request.app.state.redis.delete(redis_key)
        logger.info("验证码校验通过")

    @classmethod
    async def authenticate_user(cls, request: Request, query_db: AsyncSession, login_user: UserLogin):
        """根据用户名密码校验用户登录"""
        user = await login_by_account(query_db, login_user.user_name)
        if not user:
            logger.warning("用户不存在")
            raise LoginException(data="", message="用户不存在")
        if not PwdUtil.verify_password(login_user.password, user[0].password):
            logger.warning("密码错误")
            raise LoginException(data="", message="密码错误")
        if user[0].status == "1":
            logger.warning("用户已停用")
            raise LoginException(data="", message="用户已停用")
        return user

    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: Union[timedelta, None] = None):
        """根据登录信息创建当前用户token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, JwtConfig.jwt_secret_key, algorithm=JwtConfig.jwt_algorithm)
        return encoded_jwt

    @classmethod
    async def get_current_user(
        cls, request: Request = Request, token: str = Depends(oauth2_scheme), query_db: AsyncSession = Depends(get_db)
    ):
        """根据token获取当前用户信息"""
        try:
            if token.startswith("Bearer"):
                token = token.split(" ")[1]
            payload = jwt.decode(token, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
            user_id: str = payload.get("user_id")
            session_id: str = payload.get("session_id")
            if not user_id:
                logger.warning("用户token不合法")
                raise AuthException(data="", message="用户token不合法")
            token_data = TokenData(user_id=int(user_id))
        except InvalidTokenError:
            logger.warning("用户token已失效，请重新登录")
            raise AuthException(data="", message="用户token已失效，请重新登录")

        query_user = await UserDao.get_user_by_id(query_db, user_id=token_data.user_id)
        if query_user.get("user_basic_info") is None:
            logger.warning("用户token不合法")
            raise AuthException(data="", message="用户token不合法")

        if AppConfig.app_same_time_login:
            redis_token = await request.app.state.redis.get(f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}")
        else:
            redis_token = await request.app.state.redis.get(
                f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{query_user.get('user_basic_info').user_id}"
            )

        if token == redis_token:
            if AppConfig.app_same_time_login:
                await request.app.state.redis.set(
                    f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}",
                    redis_token,
                    ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes),
                )
            else:
                await request.app.state.redis.set(
                    f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{query_user.get('user_basic_info').user_id}",
                    redis_token,
                    ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes),
                )

            role_id_list = [item.role_id for item in query_user.get("user_role_info")]
            if 1 in role_id_list:
                permissions = ["*:*:*"]
            else:
                permissions = [row.perms for row in query_user.get("user_menu_info") if row.perms]

            post_ids = ",".join([str(row.post_id) for row in query_user.get("user_post_info")])
            role_ids = ",".join([str(row.role_id) for row in query_user.get("user_role_info")])
            roles = [row.role_key for row in query_user.get("user_role_info")]

            current_user = CurrentUserModel(
                permissions=permissions,
                roles=roles,
                user=UserInfoModel(
                    **CamelCaseUtil.transform_result(query_user.get("user_basic_info")),
                    postIds=post_ids,
                    roleIds=role_ids,
                    role=CamelCaseUtil.transform_result(query_user.get("user_role_info")),
                ),
                isDefaultModifyPwd=False,
                isPasswordExpired=False,
            )
            # 将用户信息存储到request.state，供中间件使用
            request.state.current_user = current_user
            return current_user
        else:
            logger.warning("用户token已失效，请重新登录")
            raise AuthException(data="", message="用户token已失效，请重新登录")

    @classmethod
    async def get_current_user_routers(cls, user_id: int, query_db: AsyncSession):
        """根据用户id获取当前用户路由信息"""
        query_user = await UserDao.get_user_by_id(query_db, user_id=user_id)
        user_router_menu = sorted(
            [
                row
                for row in query_user.get("user_menu_info")
                if row.menu_type in [MenuConstant.TYPE_DIR, MenuConstant.TYPE_MENU]
            ],
            key=lambda x: x.order_num,
        )
        menus = cls.__generate_menus(0, user_router_menu)
        user_router = cls.__generate_user_router_menu(menus)
        return [router.model_dump(exclude_unset=True, by_alias=True) for router in user_router]

    @classmethod
    def __generate_menus(cls, pid: int, permission_list: List[SysMenu]):
        """根据菜单信息生成菜单信息树形嵌套数据"""
        menu_list: List[MenuTreeModel] = []
        for permission in permission_list:
            if permission.parent_id == pid:
                children = cls.__generate_menus(permission.menu_id, permission_list)
                menu_list_data = MenuTreeModel(**CamelCaseUtil.transform_result(permission))
                if children:
                    menu_list_data.children = children
                menu_list.append(menu_list_data)
        return menu_list

    @classmethod
    def __generate_user_router_menu(cls, permission_list: List[MenuTreeModel]):
        """根据菜单树信息生成路由信息树形嵌套数据"""
        router_list: List[RouterModel] = []
        for permission in permission_list:
            router = RouterModel(
                hidden=True if permission.visible == "1" else False,
                name=RouterUtil.get_router_name(permission),
                path=RouterUtil.get_router_path(permission),
                component=RouterUtil.get_component(permission),
                query=permission.query,
                meta=MetaModel(
                    title=permission.menu_name,
                    icon=permission.icon,
                    noCache=True if permission.is_cache == 1 else False,
                    link=permission.path if RouterUtil.is_http(permission.path) else None,
                ),
            )
            c_menus = permission.children
            if c_menus and permission.menu_type == MenuConstant.TYPE_DIR:
                router.always_show = True
                router.redirect = "noRedirect"
                router.children = cls.__generate_user_router_menu(c_menus)
            elif RouterUtil.is_menu_frame(permission):
                router.meta = None
                children_list: List[RouterModel] = []
                children = RouterModel(
                    path=permission.path,
                    component=permission.component,
                    name=RouterUtil.get_route_name(None, permission.path),
                    meta=MetaModel(
                        title=permission.menu_name,
                        icon=permission.icon,
                        noCache=True if permission.is_cache == 1 else False,
                        link=permission.path if RouterUtil.is_http(permission.path) else None,
                    ),
                    query=permission.query,
                )
                children_list.append(children)
                router.children = children_list
            elif permission.parent_id == 0 and RouterUtil.is_inner_link(permission):
                router.meta = MetaModel(title=permission.menu_name, icon=permission.icon)
                router.path = "/"
                children_list: List[RouterModel] = []
                router_path = RouterUtil.inner_link_replace_each(permission.path)
                children = RouterModel(
                    path=router_path,
                    component=MenuConstant.INNER_LINK,
                    name=RouterUtil.get_route_name(None, permission.path),
                    meta=MetaModel(
                        title=permission.menu_name,
                        icon=permission.icon,
                        link=permission.path if RouterUtil.is_http(permission.path) else None,
                    ),
                )
                children_list.append(children)
                router.children = children_list
            router_list.append(router)
        return router_list

    @classmethod
    async def logout_services(cls, request: Request, token_id: str):
        """退出登录services"""
        await request.app.state.redis.delete(f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{token_id}")
        return True


class RouterUtil:
    """路由处理工具类"""

    @classmethod
    def get_router_name(cls, menu: MenuTreeModel):
        if cls.is_menu_frame(menu):
            return ""
        return cls.get_route_name(None, menu.path)

    @classmethod
    def get_route_name(cls, name: str, path: str):
        router_name = name if name else path
        return router_name.capitalize() if router_name else ""

    @classmethod
    def get_router_path(cls, menu: MenuTreeModel):
        router_path = menu.path
        if menu.parent_id != 0 and cls.is_inner_link(menu):
            router_path = cls.inner_link_replace_each(router_path)
        if menu.parent_id == 0 and menu.menu_type == MenuConstant.TYPE_DIR and menu.is_frame == MenuConstant.NO_FRAME:
            router_path = f"/{menu.path}"
        elif cls.is_menu_frame(menu):
            router_path = "/"
        return router_path

    @classmethod
    def get_component(cls, menu: MenuTreeModel):
        component = MenuConstant.LAYOUT
        if menu.component and not cls.is_menu_frame(menu):
            component = menu.component
        elif (menu.component is None or menu.component == "") and menu.parent_id != 0 and cls.is_inner_link(menu):
            component = MenuConstant.INNER_LINK
        elif (menu.component is None or menu.component == "") and cls.is_parent_view(menu):
            component = MenuConstant.PARENT_VIEW
        return component

    @classmethod
    def is_menu_frame(cls, menu: MenuTreeModel):
        return (
            menu.parent_id == 0 and menu.menu_type == MenuConstant.TYPE_MENU and menu.is_frame == MenuConstant.NO_FRAME
        )

    @classmethod
    def is_inner_link(cls, menu: MenuTreeModel):
        return menu.is_frame == MenuConstant.NO_FRAME and cls.is_http(menu.path)

    @classmethod
    def is_parent_view(cls, menu: MenuTreeModel):
        return menu.parent_id != 0 and menu.menu_type == MenuConstant.TYPE_DIR

    @classmethod
    def is_http(cls, link: str):
        if not link:
            return False
        return link.startswith(CommonConstant.HTTP) or link.startswith(CommonConstant.HTTPS)

    @classmethod
    def inner_link_replace_each(cls, path: str):
        old_values = [CommonConstant.HTTP, CommonConstant.HTTPS, CommonConstant.WWW, ".", ":"]
        new_values = ["", "", "", "/", "/"]
        for old, new in zip(old_values, new_values):
            path = path.replace(old, new)
        return path
