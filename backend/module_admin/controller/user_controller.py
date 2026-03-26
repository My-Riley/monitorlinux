import io
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import UploadConfig
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.entity.vo.user_vo import CurrentUserModel, EditUserModel, UserModel
from module_admin.service.login_service import LoginService
from module_admin.service.user_service import UserService
from utils.log_util import logger
from utils.response_util import ResponseUtil

# 图片上传目录 - 使用配置文件中的路径
UPLOAD_DIR = UploadConfig.UPLOAD_PATH


userController = APIRouter(prefix="/system/user", dependencies=[Depends(LoginService.get_current_user)])


@userController.get("/list")
async def get_user_list(
    request: Request,
    user_name: Optional[str] = Query(default=None, alias="userName"),
    nick_name: Optional[str] = Query(default=None, alias="nickName"),
    phonenumber: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    dept_id: Optional[int] = Query(default=None, alias="deptId"),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取用户列表"""
    page_object = UserModel(
        user_name=user_name,
        nick_name=nick_name,
        phonenumber=phonenumber,
        status=status,
        dept_id=dept_id,
    )
    result = await UserService.get_user_list_services(query_db, page_object, page_num, page_size, begin_time, end_time)
    logger.info("获取用户列表成功")
    return ResponseUtil.success(model_content=result)


@userController.get("/deptTree")
async def get_dept_tree(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """获取部门树结构"""
    try:
        tree = await UserService.get_dept_tree_services(query_db)
        logger.info("获取部门树成功")
        return ResponseUtil.success(data=tree)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.get("/authRole/{user_id}")
async def get_auth_role(
    request: Request,
    user_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取授权角色"""
    try:
        result = await UserService.get_auth_role_services(query_db, user_id)
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.put("/authRole")
async def update_auth_role(
    request: Request,
    user_id: int = Query(alias="userId"),
    role_ids: Optional[str] = Query(default=None, alias="roleIds"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """保存授权角色"""
    try:
        result = await UserService.update_auth_role_services(query_db, user_id, role_ids)
        logger.info(f"保存授权角色成功: user_id={user_id}")
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.get("/profile")
async def get_user_profile(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取用户个人信息"""
    try:
        result = await UserService.user_detail_services(query_db, current_user.user.user_id)
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.get("/{user_id}")
async def get_user_info(
    user_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取用户详细信息"""
    try:
        result = await UserService.get_user_detail_for_edit_services(query_db, user_id, current_user.user.user_id)
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.get("/")
async def get_user_for_add(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """新增用户时获取角色和岗位列表"""
    try:
        result = await UserService.get_user_for_add_services(query_db)
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.post("")
@Log(title="用户管理", business_type=1)
async def add_user(
    request: Request,
    user_data: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增用户"""
    try:
        result = await UserService.add_user_services(query_db, user_data, current_user.user.user_name, current_user.user.user_id)
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        logger.error(f"新增用户失败: {e}")
        return ResponseUtil.error(msg=str(e))


@userController.put("")
@Log(title="用户管理", business_type=2)
async def update_user(
    request: Request,
    user_data: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改用户"""
    try:
        result = await UserService.update_user_services(query_db, user_data, current_user.user.user_name, current_user.user.user_id)
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        logger.error(f"修改用户失败: {e}")
        return ResponseUtil.error(msg=str(e))


@userController.post("/export")
@Log(title="用户管理", business_type=5)
async def export_user(
    request: Request,
    user_name: Optional[str] = Form(default=None, alias="userName"),
    phonenumber: Optional[str] = Form(default=None),
    status: Optional[str] = Form(default=None),
    dept_id: Optional[int] = Form(default=None, alias="deptId"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导出用户列表"""
    query_params = {
        "user_name": user_name,
        "phonenumber": phonenumber,
        "status": status,
        "dept_id": dept_id
    }
    output = await UserService.export_user_services(query_db, query_params)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=user_list.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@userController.post("/importData")
@Log(title="用户管理", business_type=6)
async def import_data(
    request: Request,
    file: UploadFile = File(...),
    update_support: bool = Query(default=False, alias="updateSupport"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导入用户数据"""
    try:
        result = await UserService.import_data_services(query_db, file, update_support, current_user.user.user_name)
        return ResponseUtil.success(msg=result["msg"], data={"messages": result["messages"]})
    except Exception as e:
        logger.error(f"导入失败: {str(e)}")
        return ResponseUtil.error(msg="导入失败，请检查文件格式")


@userController.get("/importTemplate")
async def import_template(
    request: Request,
):
    """下载用户导入模板"""
    data = [{"用户账号": "admin", "用户昵称": "管理员", "部门ID": "100", "手机号码": "15888888888", "用户状态": "0"}]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="用户数据")
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=user_template.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@userController.put("/profile")
@Log(title="个人中心", business_type=2)
async def update_user_profile(
    request: Request,
    user_data: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改用户个人信息"""
    try:
        result = await UserService.update_profile_services(
            query_db, user_data, current_user.user.user_id, current_user.user.user_name
        )
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.put("/profile/updatePwd")
@Log(title="个人中心", business_type=2)
async def update_user_pwd(
    request: Request,
    old_password: str = Query(alias="oldPassword"),
    new_password: str = Query(alias="newPassword"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改用户密码"""
    try:
        result = await UserService.update_pwd_services(
            query_db, old_password, new_password, current_user.user.user_id, current_user.user.user_name
        )
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.put("/resetPwd")
@Log(title="用户管理", business_type=2)
async def reset_user_pwd(
    request: Request,
    user_data: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """重置用户密码"""
    try:
        result = await UserService.reset_pwd_services(query_db, user_data, current_user.user.user_name)
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.put("/changeStatus")
@Log(title="用户管理", business_type=2)
async def change_user_status(
    request: Request,
    user_data: EditUserModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改用户状态"""
    try:
        result = await UserService.change_status_services(query_db, user_data, current_user.user.user_name)
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))


@userController.delete("/{user_ids}")
@Log(title="用户管理", business_type=3)
async def delete_user(
    request: Request,
    user_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """删除用户"""
    try:
        result = await UserService.delete_user_services(
            query_db, user_ids, current_user.user.user_id, current_user.user.user_name
        )
        return ResponseUtil.success(msg=result.message)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))
