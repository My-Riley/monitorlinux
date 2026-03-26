from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_camera.entity.vo.camera_warn_vo import WarnModel
from module_camera.service.camera_warn_service import CameraWarnService
from utils.log_util import logger
from utils.response_util import ResponseUtil

warnController = APIRouter(prefix="/camera/warn", dependencies=[Depends(LoginService.get_current_user)])


@warnController.get("/list")
async def get_warn_list(
    request: Request,
    warn_name: Optional[str] = Query(default=None, alias="warnName"),
    status: Optional[str] = Query(default=None),
    warn_level: Optional[str] = Query(default=None, alias="warnLevel"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取预警列表"""
    query_params = {
        "warn_name": warn_name,
        "status": status,
        "warn_level": warn_level,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await CameraWarnService.get_warn_list_services(query_db, query_params, is_page=True)
    logger.info("获取预警列表成功")
    return ResponseUtil.success(model_content=result)


@warnController.get("/{warn_id}")
async def get_warn_detail(
    request: Request,
    warn_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取预警详情"""
    result = await CameraWarnService.get_warn_detail_services(query_db, warn_id)
    logger.info("获取预警详情成功")
    return ResponseUtil.success(data=result)


@warnController.post("")
async def add_warn(
    request: Request,
    warn_data: WarnModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增预警"""
    await CameraWarnService.add_warn_services(query_db, warn_data, current_user.user.user_name)
    logger.info("新增预警成功")
    return ResponseUtil.success(msg="新增成功")


@warnController.put("")
async def update_warn(
    request: Request,
    warn_data: WarnModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改预警"""
    await CameraWarnService.update_warn_services(query_db, warn_data, current_user.user.user_name)
    logger.info("修改预警成功")
    return ResponseUtil.success(msg="修改成功")


@warnController.delete("/{warn_id}")
async def delete_warn(
    request: Request,
    warn_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除预警"""
    warn_ids = warn_id.split(",")
    for wid in warn_ids:
        try:
            await CameraWarnService.delete_warn_services(query_db, int(wid))
        except Exception as e:
            return ResponseUtil.error(msg=str(e))
    logger.info("删除预警成功")
    return ResponseUtil.success(msg="删除成功")
