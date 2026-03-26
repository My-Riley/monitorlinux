class LoginException(Exception):
    """自定义登录异常"""

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class AuthException(Exception):
    """自定义令牌异常"""

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class PermissionException(Exception):
    """自定义权限异常"""

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class ServiceException(Exception):
    """自定义服务异常"""

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message
        super().__init__(self.message)


class ServiceWarning(Exception):
    """自定义服务警告"""

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message


class ModelValidatorException(Exception):
    """自定义模型校验异常"""

    def __init__(self, data: str = None, message: str = None):
        self.data = data
        self.message = message
