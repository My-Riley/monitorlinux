import uuid
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import RedisInitKeyConfig
from config.env import AppConfig, JwtConfig
from config.get_db import get_db
from exceptions.exception import LoginException
from module_admin.entity.vo.login_vo import Token, UserLogin
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService, oauth2_scheme
from utils.log_util import logger
from utils.response_util import ResponseUtil

loginController = APIRouter()


@loginController.post("/login", response_model=Token)
async def login(request: Request, query_db: AsyncSession = Depends(get_db)):
    # 支持JSON格式的登录请求
    body = await request.json()
    captcha_enabled = True  # 启用验证码校验
    user = UserLogin(
        userName=body.get("username", ""),
        password=body.get("password", ""),
        code=body.get("code", ""),
        uuid=body.get("uuid", ""),
        loginInfo=body.get("loginInfo"),
        captchaEnabled=captcha_enabled,
    )

    try:
        # 验证码校验（优先于用户名密码校验，防止信息泄露）
        if captcha_enabled:
            await LoginService.validate_captcha(request, user.code, user.uuid)

        result = await LoginService.authenticate_user(request, query_db, user)
    except LoginException as e:
        # 记录失败登录日志（不影响异常返回）
        await LoginService.record_logininfor(
            request=request,
            query_db=query_db,
            user_name=user.user_name,
            status="1",
            msg=e.message or "登录失败",
        )
        raise

    # 获取客户端信息
    ip = LoginService._get_client_ip(request)
    browser, os = LoginService._get_ua_info(request)
    location = LoginService._resolve_login_location_sync(ip)
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 构造登录信息
    login_info = {"ipaddr": ip, "loginLocation": location, "browser": browser, "os": os, "loginTime": login_time}

    access_token_expires = timedelta(minutes=JwtConfig.jwt_expire_minutes)
    session_id = str(uuid.uuid4())
    access_token = await LoginService.create_access_token(
        data={
            "user_id": str(result[0].user_id),
            "user_name": result[0].user_name,
            "dept_name": result[1].dept_name if result[1] else None,
            "session_id": session_id,
            "login_info": login_info,
        },
        expires_delta=access_token_expires,
    )
    if AppConfig.app_same_time_login:
        await request.app.state.redis.set(
            f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{session_id}",
            access_token,
            ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes),
        )
    else:
        await request.app.state.redis.set(
            f"{RedisInitKeyConfig.ACCESS_TOKEN.key}:{result[0].user_id}",
            access_token,
            ex=timedelta(minutes=JwtConfig.jwt_redis_expire_minutes),
        )

    # 记录成功登录日志
    await LoginService.record_logininfor(
        request=request,
        query_db=query_db,
        user_name=result[0].user_name,
        status="0",
        msg="登录成功",
    )
    logger.info("登录成功")
    request_from_swagger = request.headers.get("referer", "").endswith("docs")
    request_from_redoc = request.headers.get("referer", "").endswith("redoc")
    if request_from_swagger or request_from_redoc:
        return {"access_token": access_token, "token_type": "Bearer"}
    return ResponseUtil.success(msg="登录成功", dict_content={"token": access_token})


@loginController.get("/getInfo", response_model=CurrentUserModel)
async def get_login_user_info(
    request: Request, current_user: CurrentUserModel = Depends(LoginService.get_current_user)
):
    logger.info("获取成功")
    return ResponseUtil.success(model_content=current_user)


@loginController.get("/getRouters")
async def get_login_user_routers(
    request: Request,
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
    query_db: AsyncSession = Depends(get_db),
):
    logger.info("获取成功")
    user_routers = await LoginService.get_current_user_routers(current_user.user.user_id, query_db)
    return ResponseUtil.success(data=user_routers)


@loginController.post("/logout")
async def logout(request: Request, token: Optional[str] = Depends(oauth2_scheme)):
    payload = jwt.decode(
        token, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm], options={"verify_exp": False}
    )
    if AppConfig.app_same_time_login:
        token_id: str = payload.get("session_id")
    else:
        token_id: str = payload.get("user_id")
    await LoginService.logout_services(request, token_id)
    logger.info("退出成功")
    return ResponseUtil.success(msg="退出成功")
