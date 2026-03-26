import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.role_do import SysRole, SysRoleDept, SysRoleMenu
from module_admin.entity.do.user_do import SysUser, SysUserRole
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil

roleController = APIRouter(prefix="/system/role", dependencies=[Depends(LoginService.get_current_user)])


class RoleEditModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    role_id: Optional[int] = Field(default=None)
    role_name: Optional[str] = Field(default=None)
    role_key: Optional[str] = Field(default=None)
    role_sort: Optional[int] = Field(default=None)
    data_scope: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    menu_ids: Optional[List[int]] = Field(default=[])
    dept_ids: Optional[List[int]] = Field(default=[])
    remark: Optional[str] = Field(default=None)


@roleController.post("/export")
@Log(title="角色管理", business_type=5)
async def export_role(
    request: Request,
    role_name: Optional[str] = Form(default=None, alias="roleName"),
    role_key: Optional[str] = Form(default=None, alias="roleKey"),
    status: Optional[str] = Form(default=None),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导出角色列表"""
    query = select(SysRole).where(SysRole.del_flag == "0")
    if role_name:
        query = query.where(SysRole.role_name.like(f"%{role_name}%"))
    if role_key:
        query = query.where(SysRole.role_key.like(f"%{role_key}%"))
    if status:
        query = query.where(SysRole.status == status)
    query = query.order_by(SysRole.role_sort)

    result = await query_db.execute(query)
    roles = result.scalars().all()

    # 转换为DataFrame
    data = []
    for role in roles:
        data.append(
            {
                "角色编号": role.role_id,
                "角色名称": role.role_name,
                "权限字符": role.role_key,
                "显示顺序": role.role_sort,
                "状态": "正常" if role.status == "0" else "停用",
                "创建时间": role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else "",
            }
        )

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="角色数据")
        worksheet = writer.sheets["角色数据"]
        # 设置列宽
        for idx, col in enumerate(df.columns):
            worksheet.column_dimensions[chr(65 + idx)].width = 20

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=role_list.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@roleController.get("/list")
async def get_role_list(
    request: Request,
    role_name: Optional[str] = Query(default=None, alias="roleName"),
    role_key: Optional[str] = Query(default=None, alias="roleKey"),
    status: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取角色列表"""
    query = select(SysRole).where(SysRole.del_flag == "0")
    if role_name:
        query = query.where(SysRole.role_name.like(f"%{role_name}%"))
    if role_key:
        query = query.where(SysRole.role_key.like(f"%{role_key}%"))
    if status:
        query = query.where(SysRole.status == status)
    query = query.order_by(SysRole.role_sort)
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取角色列表成功")
    return ResponseUtil.success(model_content=result)


@roleController.get("/{role_id}")
async def get_role_detail(
    request: Request,
    role_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取角色详情"""
    query = select(SysRole).where(SysRole.role_id == role_id, SysRole.del_flag == "0")
    result = await query_db.execute(query)
    role = result.scalar()
    logger.info("获取角色详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(role))


@roleController.post("")
@Log(title="角色管理", business_type=1)
async def add_role(
    request: Request,
    role_data: RoleEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增角色"""
    role = SysRole(
        role_name=role_data.role_name,
        role_key=role_data.role_key,
        role_sort=role_data.role_sort or 0,
        data_scope=role_data.data_scope or "1",
        status=role_data.status or "0",
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
        remark=role_data.remark,
    )
    query_db.add(role)
    await query_db.commit()
    await query_db.refresh(role)

    # 添加角色菜单关联
    if role_data.menu_ids:
        for menu_id in role_data.menu_ids:
            role_menu = SysRoleMenu(role_id=role.role_id, menu_id=menu_id)
            query_db.add(role_menu)
        await query_db.commit()

    logger.info("新增角色成功")
    return ResponseUtil.success(msg="新增成功")


@roleController.put("")
@Log(title="角色管理", business_type=2)
async def update_role(
    request: Request,
    role_data: RoleEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改角色"""
    update_data = {
        "role_name": role_data.role_name,
        "role_key": role_data.role_key,
        "role_sort": role_data.role_sort,
        "data_scope": role_data.data_scope,
        "status": role_data.status,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
        "remark": role_data.remark,
    }
    query = update(SysRole).where(SysRole.role_id == role_data.role_id).values(**update_data)
    await query_db.execute(query)

    # 更新角色菜单关联
    if role_data.menu_ids is not None:
        await query_db.execute(delete(SysRoleMenu).where(SysRoleMenu.role_id == role_data.role_id))
        for menu_id in role_data.menu_ids:
            role_menu = SysRoleMenu(role_id=role_data.role_id, menu_id=menu_id)
            query_db.add(role_menu)

    await query_db.commit()
    logger.info("修改角色成功")
    return ResponseUtil.success(msg="修改成功")


@roleController.put("/dataScope")
@Log(title="角色管理", business_type=2)
async def update_data_scope(
    request: Request,
    role_data: RoleEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改角色数据权限"""
    update_data = {
        "data_scope": role_data.data_scope,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
    }
    query = update(SysRole).where(SysRole.role_id == role_data.role_id).values(**update_data)
    await query_db.execute(query)

    # 更新角色部门关联
    if role_data.dept_ids is not None:
        await query_db.execute(delete(SysRoleDept).where(SysRoleDept.role_id == role_data.role_id))
        for dept_id in role_data.dept_ids:
            role_dept = SysRoleDept(role_id=role_data.role_id, dept_id=dept_id)
            query_db.add(role_dept)

    await query_db.commit()
    logger.info("修改角色数据权限成功")
    return ResponseUtil.success(msg="修改成功")


@roleController.put("/changeStatus")
@Log(title="角色管理", business_type=2)
async def change_role_status(
    request: Request,
    role_data: RoleEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改角色状态"""
    update_data = {
        "status": role_data.status,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
    }
    query = update(SysRole).where(SysRole.role_id == role_data.role_id).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改角色状态成功")
    return ResponseUtil.success(msg="修改成功")


@roleController.delete("/{role_ids}")
@Log(title="角色管理", business_type=3)
async def delete_role(
    request: Request,
    role_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除角色"""
    ids = role_ids.split(",")
    for rid in ids:
        query = update(SysRole).where(SysRole.role_id == int(rid)).values(del_flag="2")
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除角色成功")
    return ResponseUtil.success(msg="删除成功")


@roleController.get("/authUser/allocatedList")
async def get_allocated_user_list(
    request: Request,
    role_id: int = Query(alias="roleId"),
    user_name: Optional[str] = Query(default=None, alias="userName"),
    phonenumber: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取角色已授权用户列表"""
    logger.info(f"获取角色已授权用户列表: role_id={role_id}")
    query = (
        select(SysUser)
        .join(SysUserRole, SysUser.user_id == SysUserRole.user_id)
        .where(SysUserRole.role_id == role_id, SysUser.del_flag == "0")
    )
    if user_name:
        query = query.where(SysUser.user_name.like(f"%{user_name}%"))
    if phonenumber:
        query = query.where(SysUser.phonenumber.like(f"%{phonenumber}%"))
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取角色已授权用户列表成功")
    return ResponseUtil.success(model_content=result)


@roleController.get("/authUser/unallocatedList")
async def get_unallocated_user_list(
    request: Request,
    role_id: int = Query(alias="roleId"),
    user_name: Optional[str] = Query(default=None, alias="userName"),
    phonenumber: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取角色未授权用户列表"""
    # 获取已授权用户ID
    allocated_query = select(SysUserRole.user_id).where(SysUserRole.role_id == role_id)
    allocated_result = await query_db.execute(allocated_query)
    allocated_ids = [r[0] for r in allocated_result.all()]

    query = select(SysUser).where(SysUser.del_flag == "0")
    if allocated_ids:
        query = query.where(SysUser.user_id.notin_(allocated_ids))
    if user_name:
        query = query.where(SysUser.user_name.like(f"%{user_name}%"))
    if phonenumber:
        query = query.where(SysUser.phonenumber.like(f"%{phonenumber}%"))
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取角色未授权用户列表成功")
    return ResponseUtil.success(model_content=result)


class AuthUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    role_id: Optional[int] = Field(default=None)
    user_id: Optional[int] = Field(default=None)


@roleController.put("/authUser/cancel")
@Log(title="角色管理", business_type=4)
async def cancel_auth_user(
    request: Request,
    data: AuthUserModel,
    query_db: AsyncSession = Depends(get_db),
):
    """取消用户授权角色"""
    await query_db.execute(
        delete(SysUserRole).where(SysUserRole.role_id == data.role_id, SysUserRole.user_id == data.user_id)
    )
    await query_db.commit()
    logger.info("取消用户授权角色成功")
    return ResponseUtil.success(msg="取消授权成功")


@roleController.put("/authUser/cancelAll")
@Log(title="角色管理", business_type=4)
async def cancel_auth_user_all(
    request: Request,
    role_id: int = Query(alias="roleId"),
    user_ids: str = Query(alias="userIds"),
    query_db: AsyncSession = Depends(get_db),
):
    """批量取消用户授权角色"""
    ids = user_ids.split(",")
    for uid in ids:
        await query_db.execute(
            delete(SysUserRole).where(SysUserRole.role_id == role_id, SysUserRole.user_id == int(uid))
        )
    await query_db.commit()
    logger.info("批量取消用户授权角色成功")
    return ResponseUtil.success(msg="取消授权成功")


@roleController.put("/authUser/selectAll")
@Log(title="角色管理", business_type=4)
async def select_auth_user_all(
    request: Request,
    role_id: int = Query(alias="roleId"),
    user_ids: str = Query(alias="userIds"),
    query_db: AsyncSession = Depends(get_db),
):
    """批量授权用户角色"""
    ids = user_ids.split(",")
    for uid in ids:
        user_role = SysUserRole(user_id=int(uid), role_id=role_id)
        query_db.add(user_role)
    await query_db.commit()
    logger.info("批量授权用户角色成功")
    return ResponseUtil.success(msg="授权成功")


def build_dept_tree(depts: list, parent_id: int = 0) -> List[dict]:
    """构建部门树形结构"""
    tree = []
    for dept in depts:
        if dept.parent_id == parent_id:
            node = {"id": dept.dept_id, "label": dept.dept_name}
            children = build_dept_tree(depts, dept.dept_id)
            if children:
                node["children"] = children
            tree.append(node)
    return tree


@roleController.get("/deptTree/{role_id}")
async def get_dept_tree_by_role(
    request: Request,
    role_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """根据角色ID获取部门树"""
    # 获取所有部门
    dept_query = select(SysDept).where(SysDept.del_flag == "0").order_by(SysDept.order_num)
    dept_result = await query_db.execute(dept_query)
    depts = dept_result.scalars().all()

    # 获取角色已选部门
    role_dept_query = select(SysRoleDept.dept_id).where(SysRoleDept.role_id == role_id)
    role_dept_result = await query_db.execute(role_dept_query)
    checked_keys = [r[0] for r in role_dept_result.all()]

    tree = build_dept_tree(depts)
    logger.info("获取部门树成功")
    return ResponseUtil.success(data={"depts": tree, "checkedKeys": checked_keys})
