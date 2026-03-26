from enum import Enum


class BusinessType(Enum):
    """业务操作类型"""

    OTHER = 0
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    GRANT = 4
    EXPORT = 5
    IMPORT = 6
    FORCE = 7
    GENCODE = 8
    CLEAN = 9


class OperatorType(Enum):
    """操作人类别"""

    OTHER = 0
    MANAGE = 1
    MOBILE = 2


class RedisInitKeyConfig(Enum):
    """Redis初始化Key配置"""

    SYS_DICT = ("sys_dict", "数据字典")
    SYS_CONFIG = ("sys_config", "配置信息")
    CAPTCHA_CODES = ("captcha_codes", "验证码")
    ACCESS_TOKEN = ("access_token", "登录令牌")
    ACCOUNT_LOCK = ("account_lock", "账号锁定")
    PASSWORD_ERROR_COUNT = ("password_error_count", "密码错误次数")
    SMS_CODE = ("sms_code", "短信验证码")

    def __init__(self, key: str, remark: str):
        self._key = key
        self._remark = remark

    @property
    def key(self):
        return self._key

    @property
    def remark(self):
        return self._remark
