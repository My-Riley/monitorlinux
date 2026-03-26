from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from exceptions.exception import (
    AuthException,
    LoginException,
    ModelValidatorException,
    PermissionException,
    ServiceException,
    ServiceWarning,
)
from utils.log_util import logger
from utils.response_util import ResponseUtil


def handle_exception(app: FastAPI):
    """全局异常处理"""

    @app.exception_handler(AuthException)
    async def auth_exception_handler(request: Request, exc: AuthException):
        return ResponseUtil.unauthorized(data=exc.data, msg=exc.message)

    @app.exception_handler(LoginException)
    async def login_exception_handler(request: Request, exc: LoginException):
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    @app.exception_handler(ModelValidatorException)
    async def model_validator_exception_handler(request: Request, exc: ModelValidatorException):
        logger.warning(exc.message)
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    try:
        from pydantic_validation_decorator import FieldValidationError

        @app.exception_handler(FieldValidationError)
        async def field_validation_error_handler(request: Request, exc: FieldValidationError):
            logger.warning(exc.message)
            return ResponseUtil.failure(msg=exc.message)
    except ImportError:
        pass

    @app.exception_handler(PermissionException)
    async def permission_exception_handler(request: Request, exc: PermissionException):
        return ResponseUtil.forbidden(data=exc.data, msg=exc.message)

    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        logger.error(exc.message)
        return ResponseUtil.error(data=exc.data, msg=exc.message)

    @app.exception_handler(ServiceWarning)
    async def service_warning_handler(request: Request, exc: ServiceWarning):
        logger.warning(exc.message)
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            content=jsonable_encoder({"code": exc.status_code, "msg": exc.detail}), status_code=exc.status_code
        )

    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.exception(exc)
        return ResponseUtil.error(msg=str(exc))
