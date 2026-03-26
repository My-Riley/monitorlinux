from datetime import datetime

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.notice_vo import NoticeModel, NoticeQueryModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.notice_service import NoticeService
from utils.log_util import logger
from utils.response_util import ResponseUtil

noticeController = APIRouter(prefix="/system/notice", dependencies=[Depends(LoginService.get_current_user)])


@noticeController.get("/list", tags=["通知公告"])
async def get_notice_list(
    request: Request, query_params: NoticeQueryModel = Depends(), db: AsyncSession = Depends(get_db)
):
    """获取通知公告列表"""
    result = await NoticeService.get_notice_list_services(db, query_params)
    logger.info("获取通知公告列表成功")
    return ResponseUtil.success(model_content=result)


@noticeController.post("", tags=["通知公告"])
async def add_notice(
    request: Request,
    notice: NoticeModel,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增通知公告"""
    notice.create_by = current_user.user.user_name
    await NoticeService.add_notice_services(db, notice)
    logger.info("新增通知公告成功")
    return ResponseUtil.success(msg="新增成功")


@noticeController.put("", tags=["通知公告"])
async def edit_notice(
    request: Request,
    notice: NoticeModel,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改通知公告"""
    notice.update_by = current_user.user.user_name
    notice.update_time = datetime.now()
    await NoticeService.edit_notice_services(db, notice)
    logger.info("修改通知公告成功")
    return ResponseUtil.success(msg="修改成功")


@noticeController.get("/{notice_id}", tags=["通知公告"])
async def get_notice(request: Request, notice_id: int, db: AsyncSession = Depends(get_db)):
    """获取通知公告详情"""
    result = await NoticeService.notice_detail_services(db, notice_id)
    if result:
        return ResponseUtil.success(data=result.model_dump(by_alias=True))
    return ResponseUtil.error(msg="公告不存在")


@noticeController.delete("/{notice_ids}", tags=["通知公告"])
async def delete_notice(request: Request, notice_ids: str, db: AsyncSession = Depends(get_db)):
    """删除通知公告"""
    await NoticeService.delete_notice_services(db, notice_ids)
    logger.info("删除通知公告成功")
    return ResponseUtil.success(msg="删除成功")
