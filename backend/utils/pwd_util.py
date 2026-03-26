import bcrypt


class PwdUtil:
    """密码工具类"""

    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
