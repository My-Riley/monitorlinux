from fastapi import Depends, Request

from exceptions.exception import AuthException
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService


class CheckUserInterfaceAuth:
    """
    用户接口权限校验
    """

    def __init__(self, permission: str):
        self.permission = permission

    async def __call__(self, request: Request, current_user: CurrentUserModel = Depends(LoginService.get_current_user)):
        # 权限列表为空或包含通配符，则直接通过
        if not current_user.permissions or "*:*:*" in current_user.permissions:
            return True

        if self.permission in current_user.permissions:
            return True

        raise AuthException(data="", message=f"没有权限访问 {self.permission}")
