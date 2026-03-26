from fastapi import FastAPI

from middlewares.cors_middleware import add_cors_middleware
from middlewares.operlog_middleware import OperLogMiddleware


def handle_middleware(app: FastAPI):
    """全局中间件处理"""
    add_cors_middleware(app)
    # 添加操作日志中间件（需要在CORS之后，以便能访问请求头）
    app.add_middleware(OperLogMiddleware)
