from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_camera.service.semester_cycle_service import SemesterCycleService
from utils.log_util import logger
from utils.response_util import ResponseUtil

semesterCycleController = APIRouter(
    prefix="/cell/semester/cycle", dependencies=[Depends(LoginService.get_current_user)]
)


@semesterCycleController.get("/list")
async def get_cycle_list(
    request: Request,
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学期周期列表"""
    query_params = {
        "semester_id": semester_id,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await SemesterCycleService.get_cycle_list(query_db, query_params, is_page=True)
    logger.info("获取学期周期列表成功")
    return ResponseUtil.success(model_content=result)


@semesterCycleController.get("/{cycle_id}")
async def get_cycle_detail(
    request: Request,
    cycle_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取学期周期详情"""
    result = await SemesterCycleService.get_cycle_detail(query_db, cycle_id)
    logger.info("获取学期周期详情成功")
    return ResponseUtil.success(data=result)


@semesterCycleController.post("")
async def add_cycle(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增学期周期"""
    body = await request.json()
    try:
        await SemesterCycleService.add_cycle(query_db, body, current_user.user.user_name)
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))

    logger.info("新增学期周期成功")
    return ResponseUtil.success(msg="新增成功")


@semesterCycleController.put("")
async def update_cycle(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改学期周期"""
    body = await request.json()
    cycle_id = body.get("cycleId") or body.get("id")
    if not cycle_id:
        return ResponseUtil.failure(msg="周期ID不能为空")

    await SemesterCycleService.update_cycle(query_db, int(cycle_id), body, current_user.user.user_name)
    logger.info("修改学期周期成功")
    return ResponseUtil.success(msg="修改成功")


@semesterCycleController.delete("/{cycle_id}")
async def delete_cycle(
    request: Request,
    cycle_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除学期周期"""
    cycle_ids = cycle_id.split(",")
    for cid in cycle_ids:
        try:
            await SemesterCycleService.delete_cycle(query_db, int(cid))
        except Exception as e:
            return ResponseUtil.error(msg=str(e))
    logger.info("删除学期周期成功")
    return ResponseUtil.success(msg="删除成功")
