from datetime import datetime
from typing import Any, Dict, Mapping, Optional

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from config.constant import HttpStatusConstant


class ResponseUtil:
    """响应工具类"""

    @classmethod
    def success(
        cls,
        msg: str = "操作成功",
        data: Optional[Any] = None,
        rows: Optional[Any] = None,
        dict_content: Optional[Dict] = None,
        model_content: Optional[BaseModel] = None,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
    ) -> Response:
        result = {"code": HttpStatusConstant.SUCCESS, "msg": msg}
        if data is not None:
            result["data"] = data
        if rows is not None:
            result["rows"] = rows
        if dict_content is not None:
            result.update(dict_content)
        if model_content is not None:
            result.update(model_content.model_dump(by_alias=True))
        result.update({"success": True, "time": datetime.now()})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result),
            headers=headers,
            media_type=media_type,
            background=background,
        )

    @classmethod
    def failure(
        cls,
        msg: str = "操作失败",
        data: Optional[Any] = None,
        rows: Optional[Any] = None,
        dict_content: Optional[Dict] = None,
        model_content: Optional[BaseModel] = None,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None,
    ) -> Response:
        result = {"code": HttpStatusConstant.WARN, "msg": msg}
        if data is not None:
            result["data"] = data
        if rows is not None:
            result["rows"] = rows
        if dict_content is not None:
            result.update(dict_content)
        if model_content is not None:
            result.update(model_content.model_dump(by_alias=True))
        result.update({"success": False, "time": datetime.now()})
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(result),
            headers=headers,
            media_type=media_type,
            background=background,
        )

    @classmethod
    def unauthorized(
        cls, msg: str = "登录信息已过期，访问系统资源失败", data: Optional[Any] = None, **kwargs
    ) -> Response:
        result = {"code": HttpStatusConstant.UNAUTHORIZED, "msg": msg}
        if data is not None:
            result["data"] = data
        result.update({"success": False, "time": datetime.now()})
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(result))

    @classmethod
    def forbidden(cls, msg: str = "该用户无此接口权限", data: Optional[Any] = None, **kwargs) -> Response:
        result = {"code": HttpStatusConstant.FORBIDDEN, "msg": msg}
        if data is not None:
            result["data"] = data
        result.update({"success": False, "time": datetime.now()})
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(result))

    @classmethod
    def error(cls, msg: str = "接口异常", data: Optional[Any] = None, **kwargs) -> Response:
        result = {"code": HttpStatusConstant.ERROR, "msg": msg}
        if data is not None:
            result["data"] = data
        result.update({"success": False, "time": datetime.now()})
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(result))

    @classmethod
    def streaming(cls, *, data: Any = None, headers: Optional[Mapping[str, str]] = None, **kwargs) -> Response:
        def iter_file():
            yield data

        return StreamingResponse(status_code=status.HTTP_200_OK, content=iter_file(), headers=headers)
