import jwt
from fastapi import Request

from config.enums import RedisInitKeyConfig
from config.env import AppConfig, JwtConfig
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.online_vo import DeleteOnlineModel, OnlineQueryModel
from utils.common_util import CamelCaseUtil


class OnlineService:
    """
    在线用户管理模块服务层
    """

    @classmethod
    async def get_online_list_services(cls, request: Request, query_object: OnlineQueryModel):
        """
        获取在线用户表信息
        """
        access_token_keys = await request.app.state.redis.keys(f"{RedisInitKeyConfig.ACCESS_TOKEN.key}*")
        if not access_token_keys:
            access_token_keys = []

        # 批量获取
        if not access_token_keys:
            return []

        # 注意: mget 需要 keys 列表，但 redis.keys 返回的是 bytes 或 str (取决于 decode_responses)
        # 假设这里是 list[str]
        access_token_values_list = []
        for key in access_token_keys:
            val = await request.app.state.redis.get(key)
            if val:
                access_token_values_list.append(val)

        online_info_list = []
        for item in access_token_values_list:
            try:
                payload = jwt.decode(item, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
                login_info = payload.get("login_info") or {}

                # 根据配置决定token_id的值（用于强退）
                if AppConfig.app_same_time_login:
                    token_id = payload.get("session_id")
                else:
                    token_id = payload.get("user_id")

                online_dict = dict(
                    token_id=token_id,
                    user_name=payload.get("user_name"),
                    dept_name=payload.get("dept_name"),
                    ipaddr=login_info.get("ipaddr"),
                    login_location=login_info.get("loginLocation"),
                    browser=login_info.get("browser"),
                    os=login_info.get("os"),
                    login_time=login_info.get("loginTime"),
                )

                # 过滤逻辑
                match = True
                if query_object.user_name and query_object.user_name != payload.get("user_name"):
                    match = False
                if query_object.ipaddr and query_object.ipaddr != login_info.get("ipaddr"):
                    match = False

                if match:
                    online_info_list.append(online_dict)
            except Exception:
                continue

        return CamelCaseUtil.transform_result(online_info_list)

    @classmethod
    async def delete_online_services(cls, request: Request, page_object: DeleteOnlineModel):
        """
        强退在线用户
        """
        if page_object.token_ids:
            token_id_list = page_object.token_ids.split(",")
            for token_id in token_id_list:
                await request.app.state.redis.delete(f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{token_id}")
            return CrudResponseModel(is_success=True, message="强退成功")
        else:
            raise ServiceException(message="传入session_id为空")
