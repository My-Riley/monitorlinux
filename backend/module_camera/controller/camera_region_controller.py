from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_camera.dao.camera_region_dao import RegionDao
from module_camera.entity.vo.camera_region_vo import RegionModel
from module_camera.service.camera_region_service import RegionService
from utils.log_util import logger
from utils.response_util import ResponseUtil

regionController = APIRouter(prefix="/camera/region", dependencies=[Depends(LoginService.get_current_user)])


@regionController.get("/list")
async def get_region_list(
    request: Request,
    region_name: Optional[str] = Query(default=None, alias="deptName"),  # 保持前端别名
    status: Optional[str] = Query(default=None),
    query_db: AsyncSession = Depends(get_db),
):
    """获取区域列表"""
    query_params = {"region_name": region_name, "status": status}
    result = await RegionService.get_region_tree_services(query_db, query_params)
    logger.info("获取区域列表成功")
    return ResponseUtil.success(data=result)


@regionController.get("/tree")
async def get_region_tree(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """获取区域树结构"""
    result = await RegionService.get_region_tree_services(query_db, {})
    logger.info("获取区域树成功")
    return ResponseUtil.success(data=result)


@regionController.get("/{region_id}")
async def get_region_detail(
    request: Request,
    region_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取区域详情"""
    from utils.common_util import CamelCaseUtil

    result = await RegionDao.get_region_by_id(query_db, region_id)
    logger.info("获取区域详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(result))


@regionController.post("")
async def add_region(
    request: Request,
    region_data: RegionModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增区域"""
    await RegionService.add_region_services(query_db, region_data, current_user.user.user_name)
    logger.info("新增区域成功")
    return ResponseUtil.success(msg="新增成功")


@regionController.put("")
async def update_region(
    request: Request,
    region_data: RegionModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改区域"""
    await RegionService.update_region_services(query_db, region_data, current_user.user.user_name)
    logger.info("修改区域成功")
    return ResponseUtil.success(msg="修改成功")


@regionController.delete("/{region_id}")
async def delete_region(
    request: Request,
    region_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除区域"""
    region_ids = region_id.split(",")
    for rid in region_ids:
        try:
            await RegionService.delete_region_services(query_db, int(rid))
        except Exception as e:
            return ResponseUtil.error(msg=str(e))
    logger.info("删除区域成功")
    return ResponseUtil.success(msg="删除成功")
