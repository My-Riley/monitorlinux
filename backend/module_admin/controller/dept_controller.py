# dept_controller.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.user_vo import CurrentUserModel, DeptModel
from module_admin.service.login_service import LoginService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.response_util import ResponseUtil

deptController = APIRouter(prefix="/system/dept", dependencies=[Depends(LoginService.get_current_user)])


def build_dept_tree(depts: list, parent_id: int = 0) -> List[dict]:
    """构建部门树形结构"""
    tree = []
    for dept in depts:
        if dept.parent_id == parent_id:
            node = CamelCaseUtil.transform_result(dept)
            children = build_dept_tree(depts, dept.dept_id)
            if children:
                node["children"] = children
            tree.append(node)
    return tree


@deptController.get("/list")
async def get_dept_list(
    request: Request,
    dept_name: Optional[str] = Query(default=None, alias="deptName"),
    status: Optional[str] = Query(default=None),
    query_db: AsyncSession = Depends(get_db),
):
    """获取部门列表"""
    query = select(SysDept).where(SysDept.del_flag == "0")
    if dept_name:
        query = query.where(SysDept.dept_name.like(f"%{dept_name}%"))
    if status:
        query = query.where(SysDept.status == status)
    query = query.order_by(SysDept.order_num)
    result = await query_db.execute(query)
    depts = result.scalars().all()
    logger.info("获取部门列表成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(depts))


@deptController.get("/list/exclude/{dept_id}")
async def get_dept_list_exclude(
    request: Request,
    dept_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取部门列表（排除节点）"""
    query = select(SysDept).where(SysDept.del_flag == "0", SysDept.dept_id != dept_id)
    query = query.order_by(SysDept.order_num)
    result = await query_db.execute(query)
    depts = result.scalars().all()
    # 排除子节点
    filtered = [d for d in depts if str(dept_id) not in (d.ancestors or "").split(",")]
    logger.info("获取部门列表成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(filtered))


@deptController.get("/{dept_id}")
async def get_dept_detail(
    request: Request,
    dept_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取部门详情"""
    query = select(SysDept).where(SysDept.dept_id == dept_id, SysDept.del_flag == "0")
    result = await query_db.execute(query)
    dept = result.scalar()
    logger.info("获取部门详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(dept))


@deptController.post("")
@Log(title="部门管理", business_type=1)
async def add_dept(
    request: Request,
    dept_data: DeptModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增部门"""
    # 获取父部门信息
    ancestors = "0"
    if dept_data.parent_id and dept_data.parent_id > 0:
        parent_query = select(SysDept).where(SysDept.dept_id == dept_data.parent_id)
        parent_result = await query_db.execute(parent_query)
        parent = parent_result.scalar()
        if parent:
            ancestors = f"{parent.ancestors},{parent.dept_id}"

    dept = SysDept(
        parent_id=dept_data.parent_id or 0,
        ancestors=ancestors,
        dept_name=dept_data.dept_name,
        order_num=dept_data.order_num or 0,
        leader=dept_data.leader,
        phone=dept_data.phone,
        email=dept_data.email,
        status=dept_data.status or "0",
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
    )
    query_db.add(dept)
    await query_db.commit()
    logger.info("新增部门成功")
    return ResponseUtil.success(msg="新增成功")


@deptController.get("/tree")
async def get_dept_tree(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """获取部门树结构"""
    query = select(SysDept).where(SysDept.del_flag == "0").order_by(SysDept.order_num)
    result = await query_db.execute(query)
    depts = result.scalars().all()
    tree = build_dept_tree(depts)
    logger.info("获取部门树成功")
    return ResponseUtil.success(data=tree)


@deptController.put("")
@Log(title="部门管理", business_type=2)
async def update_dept(
    request: Request,
    dept_data: DeptModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改部门"""
    update_data = {
        "parent_id": dept_data.parent_id,
        "dept_name": dept_data.dept_name,
        "order_num": dept_data.order_num,
        "leader": dept_data.leader,
        "phone": dept_data.phone,
        "email": dept_data.email,
        "status": dept_data.status,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
    }
    query = update(SysDept).where(SysDept.dept_id == dept_data.dept_id).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改部门成功")
    return ResponseUtil.success(msg="修改成功")


@deptController.delete("/{dept_id}")
@Log(title="部门管理", business_type=3)
async def delete_dept(
    request: Request,
    dept_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """删除部门"""
    # 检查是否存在子部门
    child_query = select(SysDept).where(SysDept.parent_id == dept_id, SysDept.del_flag == "0")
    child_result = await query_db.execute(child_query)
    if child_result.scalars().first():
        return ResponseUtil.error(msg="存在下级部门,不允许删除")

    # 检查是否存在关联用户
    user_query = select(SysUser).where(SysUser.dept_id == dept_id, SysUser.del_flag == "0")
    user_result = await query_db.execute(user_query)
    if user_result.scalars().first():
        return ResponseUtil.error(msg="部门下存在用户,不允许删除")

    query = update(SysDept).where(SysDept.dept_id == dept_id).values(del_flag="2")
    await query_db.execute(query)
    await query_db.commit()
    logger.info("删除部门成功")
    return ResponseUtil.success(msg="删除成功")
