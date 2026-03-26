import re
from typing import Any

import bcrypt


class CamelCaseUtil:
    """驼峰命名转换工具类"""

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        """下划线转驼峰"""
        components = snake_str.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    @staticmethod
    def to_snake_case(camel_str: str) -> str:
        """驼峰转下划线"""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()

    @classmethod
    def transform_result(cls, result: Any) -> Any:
        """转换查询结果为驼峰命名"""
        if result is None:
            return None
        if isinstance(result, list):
            return [cls.transform_result(item) for item in result]
        if isinstance(result, dict):
            return {cls.to_camel_case(k): cls.transform_result(v) for k, v in result.items()}
        if hasattr(result, "__dict__"):
            return {
                cls.to_camel_case(k): cls.transform_result(v)
                for k, v in result.__dict__.items()
                if not k.startswith("_")
            }
        return result


class SqlalchemyUtil:
    """SQLAlchemy工具类"""

    @staticmethod
    def get_server_default_null(db_type: str, is_string: bool = True) -> str:
        if db_type == "postgresql":
            return None
        return "''" if is_string else None


def worship():
    """启动时打印Logo"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║     情绪识别监控系统 - Emotion Recognition Monitor System     ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()


def bytes2file_response(file_bytes):
    """字节转文件响应"""
    yield file_bytes


class PwdUtil:
    """密码工具类"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        # 确保密码不超过72字节
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def bytes2human(n):
    """
    将字节大小转换为易读的格式（B, KB, MB, GB...）
    """
    symbols = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i * 10)
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.2f%s" % (value, s)
    return "0B"
