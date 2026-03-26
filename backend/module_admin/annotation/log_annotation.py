from functools import wraps

from fastapi import Request


class Log:
    """
    操作日志注解
    """

    def __init__(self, title: str, business_type: int):
        self.title = title
        self.business_type = business_type

    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取 Request 对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request and "request" in kwargs:
                request = kwargs["request"]

            if request:
                # 将注解信息存储到 request.state 中，供 Service 层使用
                request.state.oper_log_title = self.title
                request.state.oper_log_business_type = self.business_type

            return await func(*args, **kwargs)

        return wrapper
