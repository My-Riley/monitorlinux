from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_camera.service.camera_service import CameraService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.response_util import ResponseUtil

cameraController = APIRouter(prefix="/camera/camera", dependencies=[Depends(LoginService.get_current_user)])


@cameraController.get("/list")
async def get_camera_list(
    request: Request,
    camera_name: Optional[str] = Query(default=None, alias="cameraName"),
    status: Optional[str] = Query(default=None, alias="status"),
    region_id: Optional[str] = Query(default=None, alias="regionId"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取摄像头列表"""
    # 兼容旧参数 liftName
    if not camera_name:
        camera_name = request.query_params.get("liftName")

    query_params = {
        "camera_name": camera_name,
        "status": status,
        "region_id": region_id,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await CameraService.get_camera_list(query_db, query_params, is_page=True)
    logger.info("获取摄像头列表成功")
    return ResponseUtil.success(model_content=result)


@cameraController.get("/list/{region_id}")
async def get_camera_by_region(
    request: Request,
    region_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """根据区域ID获取摄像头列表"""
    result = await CameraService.get_camera_by_region(query_db, region_id)
    logger.info("获取摄像头列表成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(result))


@cameraController.get("/{camera_id}")
async def get_camera_detail(
    request: Request,
    camera_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取摄像头详情"""
    result = await CameraService.get_camera_detail(query_db, camera_id)
    logger.info("获取摄像头详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(result))


@cameraController.post("")
async def add_camera(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增摄像头"""
    body = await request.json()
    try:
        await CameraService.add_camera(query_db, body, current_user.user.user_name)
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))

    logger.info("新增摄像头成功")
    return ResponseUtil.success(msg="新增成功")


@cameraController.put("")
async def update_camera(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改摄像头"""
    body = await request.json()
    camera_id = body.get("cameraId") or body.get("id")
    if not camera_id:
        return ResponseUtil.failure(msg="摄像头ID不能为空")

    await CameraService.update_camera(query_db, int(camera_id), body, current_user.user.user_name)
    logger.info("修改摄像头成功")
    return ResponseUtil.success(msg="修改成功")


@cameraController.delete("/{camera_id}")
async def delete_camera(
    request: Request,
    camera_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除摄像头"""
    try:
        await CameraService.delete_camera(query_db, camera_id)
    except Exception as e:
        return ResponseUtil.error(msg=str(e))
    logger.info("删除摄像头成功")
    return ResponseUtil.success(msg="删除成功")
