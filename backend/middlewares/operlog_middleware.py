import json
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from config.database import AsyncSessionLocal
from module_admin.dao.user_dao import UserDao
from module_admin.service.oper_log_service import OperLogService
from utils.log_util import logger


async def _record_oper_log_background(
    request: Request,
    oper_name: str,
    oper_url: str,
    request_method: str,
    oper_param: str,
    status: int,
    error_msg: str,
    cost_time: int,
    dept_name: str,
    json_result: str,
    method: str,
):
    """后台任务：记录操作日志"""
    try:
        async with AsyncSessionLocal() as db_session:
            await OperLogService.record_oper_log(
                request=request,
                query_db=db_session,
                oper_name=oper_name,
                oper_url=oper_url,
                request_method=request_method,
                oper_param=oper_param,
                json_result=json_result,  # 响应内容
                status=status,
                error_msg=error_msg,
                cost_time=cost_time,
                dept_name=dept_name,
                method=method,
            )
    except Exception as e:
        logger.error(f"后台记录操作日志失败: {e}")


class OperLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件：自动记录API请求的操作日志"""

    # 只记录“主要操作”的HTTP方法（默认不记录 GET/HEAD/OPTIONS）
    MAJOR_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    # 少量 GET 也属于“主要操作”的白名单（导出/导入/清理/强退等）
    # 说明：这里用“包含关键字”的粗粒度匹配，便于覆盖不同模块的导出/导入实现
    MAJOR_GET_KEYWORDS = (
        "export",
        "import",
        "clean",
        "remove",
        "delete",
        "force",
        "logout",
        "reset",
    )

    # 排除的路径（不记录日志）
    EXCLUDE_PATHS = {
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon.ico",
        "/login",
        "/captchaImage",
        "/logout",
        "/getInfo",
        "/getRouters",
        "/monitor/operlog/list",  # 避免记录操作日志查询本身
        "/monitor/logininfor/list",  # 避免记录登录日志查询本身
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """拦截请求并记录操作日志"""
        # 检查是否应该记录日志
        path = request.url.path
        if any(path.startswith(exclude) for exclude in self.EXCLUDE_PATHS):
            return await call_next(request)

        # 只记录需要认证的接口（有Authorization头）
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if not auth_header:
            return await call_next(request)

        # 只记录主要操作：
        # - 非 GET 类：POST/PUT/PATCH/DELETE
        # - GET 类：仅当路径命中“导出/导入/清空/强退”等关键字
        method_upper = request.method.upper()
        if method_upper not in self.MAJOR_METHODS:
            if method_upper == "GET" and any(k in path.lower() for k in self.MAJOR_GET_KEYWORDS):
                pass
            else:
                return await call_next(request)

        # 记录开始时间
        start_time = time.time()

        # 获取请求参数（需要在call_next之前，因为body只能读取一次）
        oper_param = ""
        try:
            if request.method in ("POST", "PUT", "PATCH"):
                body = await request.body()
                if body:
                    try:
                        # 尝试解析JSON
                        oper_param = json.dumps(json.loads(body.decode("utf-8")), ensure_ascii=False)
                    except Exception:
                        # 非JSON格式，直接使用原始字符串（限制长度）
                        oper_param = body.decode("utf-8", errors="ignore")[:500]
            elif request.method in ("GET", "DELETE"):
                # GET/DELETE请求参数在query string中
                if request.url.query:
                    oper_param = request.url.query
        except Exception as e:
            logger.warning(f"获取请求参数失败: {e}")

        # 执行请求（此时依赖注入会执行，用户信息会被设置到request.state）
        status = OperLogService.STATUS_SUCCESS
        error_msg = ""
        json_result = ""

        try:
            # 捕获响应体
            response = await call_next(request)

            if response.status_code != 200:
                # 非200状态码视为失败
                status = OperLogService.STATUS_FAIL
                error_msg = f"HTTP {response.status_code}"

            # 尝试读取响应体（注意：这可能会影响性能，且对于流式响应可能不适用）
            # 这里简单处理：如果是JSON响应，尝试读取
            # 注意：FastAPI/Starlette的Response对象一旦发送就不能再读取body，
            # 除非我们在call_next之前包装了response，或者使用background task记录日志时传递了body。
            # 但call_next返回的是Response对象，此时body可能已经被消耗或准备发送。
            # 为了获取body，我们需要自定义Response或使用iterate_in_threadpool

            # 由于FastAPI middleware机制，获取response body比较困难，这里简化处理：
            # 如果是StreamingResponse，我们很难获取完整body而不破坏流。
            # 如果是普通Response/JSONResponse，body在body属性中。

            response_content_type = response.headers.get("content-type", "")
            if "application/json" in response_content_type or "text/" in response_content_type:
                if hasattr(response, "body_iterator"):
                    try:
                        import starlette.concurrency

                        # 消耗body_iterator
                        chunks = []
                        async for chunk in response.body_iterator:
                            chunks.append(chunk)

                        response_body = b"".join(chunks)

                        # 重新填充body_iterator
                        response.body_iterator = starlette.concurrency.iterate_in_threadpool(iter([response_body]))

                        if response_body:
                            json_result = response_body.decode("utf-8", errors="ignore")[:2000]
                    except Exception:
                        pass
                elif hasattr(response, "body"):
                    try:
                        body_bytes = response.body
                        if body_bytes:
                            json_result = body_bytes.decode("utf-8", errors="ignore")[:2000]
                    except Exception:
                        pass

        except Exception as e:
            # 请求处理失败
            status = OperLogService.STATUS_FAIL
            error_msg = str(e)[:500]
            # 重新抛出异常，让全局异常处理器处理
            raise

        # 计算消耗时间（毫秒）
        cost_time = int((time.time() - start_time) * 1000)

        # 获取方法名称
        method_name = ""
        try:
            # 尝试从request.scope['endpoint']获取处理函数
            if "endpoint" in request.scope:
                endpoint = request.scope["endpoint"]
                if hasattr(endpoint, "__name__"):
                    method_name = endpoint.__name__
        except Exception:
            pass

        # 在响应后获取用户信息（此时依赖注入已完成）
        oper_name = ""
        dept_name = ""
        try:
            # 1) 优先从request.state获取（由LoginService.get_current_user设置）
            if hasattr(request.state, "current_user") and request.state.current_user:
                current_user = request.state.current_user
                oper_name = current_user.user.user_name if current_user.user else ""
                dept_name = current_user.user.dept.dept_name if current_user.user and current_user.user.dept else ""
            else:
                # 2) 如果state中没有，解析token拿到user_id，再查库获取user_name
                import jwt

                from config.env import JwtConfig

                user_id = None
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                else:
                    token = auth_header
                try:
                    payload = jwt.decode(
                        token,
                        JwtConfig.jwt_secret_key,
                        algorithms=[JwtConfig.jwt_algorithm],
                        options={"verify_signature": False},
                    )
                    user_id = payload.get("user_id")
                except Exception:
                    user_id = None

                if user_id:
                    try:
                        async with AsyncSessionLocal() as db_session:
                            user_info = await UserDao.get_user_by_id(db_session, user_id=int(user_id))
                            if user_info and user_info.get("user_basic_info"):
                                oper_name = user_info.get("user_basic_info").user_name
                            if (
                                user_info
                                and user_info.get("user_dept_info")
                                and user_info.get("user_dept_info").dept_name
                            ):
                                dept_name = user_info.get("user_dept_info").dept_name
                    except Exception:
                        pass
        except Exception:
            # 解析失败，继续记录日志（用户名为空）
            pass

        # 使用后台任务记录操作日志（不阻塞响应）
        import asyncio

        asyncio.create_task(
            _record_oper_log_background(
                request=request,
                oper_name=oper_name,
                oper_url=str(request.url.path),
                request_method=request.method,
                oper_param=oper_param,
                status=status,
                error_msg=error_msg,
                cost_time=cost_time,
                dept_name=dept_name,
                json_result=json_result,
                method=method_name,
            )
        )

        return response
