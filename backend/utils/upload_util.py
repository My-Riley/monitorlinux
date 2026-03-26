import random
import string


class UploadUtil:
    """上传工具类"""

    @staticmethod
    def generate_random_number(length: int = 4) -> str:
        """生成随机数字"""
        return "".join(random.choices(string.digits, k=length))
