from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_camera.service.emotion_anxiety_mapping_service import EmotionAnxietyMappingService
from utils.log_util import logger
from utils.response_util import ResponseUtil

mappingController = APIRouter(prefix="/system/emotion/mapping", dependencies=[Depends(LoginService.get_current_user)])


@mappingController.get("/list")
async def get_mapping_list(
    request: Request,
    emotion_en: Optional[str] = Query(default=None, alias="emotionEn"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取情绪焦虑映射列表"""
    query_params = {
        "emotion_en": emotion_en,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await EmotionAnxietyMappingService.get_mapping_list(query_db, query_params, is_page=True)
    logger.info("获取情绪焦虑映射列表成功")
    return ResponseUtil.success(model_content=result)


@mappingController.get("/{mapping_id}")
async def get_mapping_detail(
    request: Request,
    mapping_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取情绪焦虑映射详情"""
    result = await EmotionAnxietyMappingService.get_mapping_detail(query_db, mapping_id)
    logger.info("获取情绪焦虑映射详情成功")
    return ResponseUtil.success(data=result)


@mappingController.post("")
async def add_mapping(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """新增情绪焦虑映射"""
    body = await request.json()
    await EmotionAnxietyMappingService.add_mapping(query_db, body)
    logger.info("新增情绪焦虑映射成功")
    return ResponseUtil.success(msg="新增成功")


@mappingController.put("")
async def update_mapping(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """修改情绪焦虑映射"""
    body = await request.json()
    mapping_id = body.get("mappingId") or body.get("id")
    if not mapping_id:
        return ResponseUtil.failure(msg="映射ID不能为空")

    await EmotionAnxietyMappingService.update_mapping(query_db, int(mapping_id), body)
    logger.info("修改情绪焦虑映射成功")
    return ResponseUtil.success(msg="修改成功")


@mappingController.delete("/{mapping_id}")
async def delete_mapping(
    request: Request,
    mapping_id: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除情绪焦虑映射"""
    ids = mapping_id.split(",")
    for mid in ids:
        try:
            await EmotionAnxietyMappingService.delete_mapping(query_db, int(mid))
        except Exception as e:
            return ResponseUtil.error(msg=str(e))
    logger.info("删除情绪焦虑映射成功")
    return ResponseUtil.success(msg="删除成功")
