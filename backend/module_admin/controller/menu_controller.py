from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.do.role_do import SysRoleMenu
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.response_util import ResponseUtil

menuController = APIRouter(prefix="/system/menu", dependencies=[Depends(LoginService.get_current_user)])


class MenuEditModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, extra="ignore", populate_by_name=True)
    menu_id: Optional[int] = Field(default=None, alias="menuId")
    menu_name: Optional[str] = Field(default=None, alias="menuName")
    parent_id: Optional[int] = Field(default=None, alias="parentId")
    order_num: Optional[int] = Field(default=None, alias="orderNum")
    path: Optional[str] = Field(default=None)
    component: Optional[str] = Field(default=None)
    query: Optional[str] = Field(default=None)
    is_frame: Optional[str] = Field(default=None, alias="isFrame")
    is_cache: Optional[str] = Field(default=None, alias="isCache")
    menu_type: Optional[str] = Field(default=None, alias="menuType")
    visible: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    perms: Optional[str] = Field(default=None)
    icon: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)
    # 以下字段前端可能会发送，但更新时不需要处理
    create_by: Optional[str] = Field(default=None, alias="createBy")
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_by: Optional[str] = Field(default=None, alias="updateBy")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    children: Optional[list] = Field(default=None)


def build_menu_tree(menus: list, parent_id: int = 0) -> List[dict]:
    """构建菜单树形结构"""
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            node = CamelCaseUtil.transform_result(menu)
            children = build_menu_tree(menus, menu.menu_id)
            if children:
                node["children"] = children
            tree.append(node)
    return tree


def build_menu_tree_select(menus: list, parent_id: int = 0) -> List[dict]:
    """构建菜单下拉树"""
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            node = {"id": menu.menu_id, "label": menu.menu_name}
            children = build_menu_tree_select(menus, menu.menu_id)
            if children:
                node["children"] = children
            tree.append(node)
    return tree


@menuController.get("/list")
async def get_menu_list(
    request: Request,
    menu_name: Optional[str] = Query(default=None, alias="menuName"),
    status: Optional[str] = Query(default=None),
    query_db: AsyncSession = Depends(get_db),
):
    """获取菜单列表"""
    query = select(SysMenu)
    if menu_name:
        query = query.where(SysMenu.menu_name.like(f"%{menu_name}%"))
    if status:
        query = query.where(SysMenu.status == status)
    query = query.order_by(SysMenu.order_num)
    result = await query_db.execute(query)
    menus = result.scalars().all()
    logger.info("获取菜单列表成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(menus))


@menuController.get("/treeselect")
async def get_menu_tree_select(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """获取菜单下拉树"""
    query = select(SysMenu).where(SysMenu.status == "0").order_by(SysMenu.order_num)
    result = await query_db.execute(query)
    menus = result.scalars().all()
    tree = build_menu_tree_select(menus)
    logger.info("获取菜单下拉树成功")
    return ResponseUtil.success(data=tree)


@menuController.get("/roleMenuTreeselect/{role_id}")
async def get_role_menu_tree_select(
    request: Request,
    role_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """根据角色ID获取菜单下拉树"""
    # 获取所有菜单
    menu_query = select(SysMenu).where(SysMenu.status == "0").order_by(SysMenu.order_num)
    menu_result = await query_db.execute(menu_query)
    menus = menu_result.scalars().all()

    # 获取角色已选菜单
    role_menu_query = select(SysRoleMenu.menu_id).where(SysRoleMenu.role_id == role_id)
    role_menu_result = await query_db.execute(role_menu_query)
    checked_keys = [r[0] for r in role_menu_result.all()]

    tree = build_menu_tree_select(menus)
    logger.info("获取角色菜单下拉树成功")
    return ResponseUtil.success(data={"menus": tree, "checkedKeys": checked_keys})


@menuController.get("/{menu_id}")
async def get_menu_detail(
    request: Request,
    menu_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取菜单详情"""
    query = select(SysMenu).where(SysMenu.menu_id == menu_id)
    result = await query_db.execute(query)
    menu = result.scalar()
    logger.info("获取菜单详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(menu))


@menuController.post("")
@Log(title="菜单管理", business_type=1)
async def add_menu(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增菜单"""
    # 直接从请求体获取JSON数据
    body = await request.json()
    logger.info(f"收到菜单新增请求: {body}")

    menu = SysMenu(
        menu_name=body.get("menuName"),
        parent_id=body.get("parentId") or 0,
        order_num=body.get("orderNum") or 0,
        path=body.get("path"),
        component=body.get("component"),
        query=body.get("query"),
        is_frame=body.get("isFrame") or "1",
        is_cache=body.get("isCache") or "0",
        menu_type=body.get("menuType"),
        visible=body.get("visible") or "0",
        status=body.get("status") or "0",
        perms=body.get("perms"),
        icon=body.get("icon"),
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
        remark=body.get("remark"),
    )
    query_db.add(menu)
    await query_db.commit()
    logger.info("新增菜单成功")
    return ResponseUtil.success(msg="新增成功")


@menuController.put("")
@Log(title="菜单管理", business_type=2)
async def update_menu(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改菜单"""
    # 直接从请求体获取JSON数据
    body = await request.json()
    logger.info(f"收到菜单更新请求: {body}")

    update_data = {
        "menu_name": body.get("menuName"),
        "parent_id": body.get("parentId"),
        "order_num": body.get("orderNum"),
        "path": body.get("path"),
        "component": body.get("component"),
        "query": body.get("query"),
        "is_frame": body.get("isFrame"),
        "is_cache": body.get("isCache"),
        "menu_type": body.get("menuType"),
        "visible": body.get("visible"),
        "status": body.get("status"),
        "perms": body.get("perms"),
        "icon": body.get("icon"),
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
        "remark": body.get("remark"),
    }
    menu_id = body.get("menuId")
    query = update(SysMenu).where(SysMenu.menu_id == menu_id).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改菜单成功")
    return ResponseUtil.success(msg="修改成功")


@menuController.delete("/{menu_id}")
@Log(title="菜单管理", business_type=3)
async def delete_menu(
    request: Request,
    menu_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """删除菜单"""
    query = delete(SysMenu).where(SysMenu.menu_id == menu_id)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("删除菜单成功")
    return ResponseUtil.success(msg="删除成功")
