import io
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from config.get_redis import RedisUtil
from module_admin.annotation.log_annotation import Log
from module_admin.entity.do.config_do import SysConfig
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil

configController = APIRouter(prefix="/system/config", dependencies=[Depends(LoginService.get_current_user)])


class ConfigEditModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    config_id: Optional[int] = Field(default=None)
    config_name: Optional[str] = Field(default=None)
    config_key: Optional[str] = Field(default=None)
    config_value: Optional[str] = Field(default=None)
    config_type: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)


@configController.get("/list")
async def get_config_list(
    request: Request,
    config_name: Optional[str] = Query(default=None, alias="configName"),
    config_key: Optional[str] = Query(default=None, alias="configKey"),
    config_type: Optional[str] = Query(default=None, alias="configType"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取参数配置列表"""
    query = select(SysConfig)
    if config_name:
        query = query.where(SysConfig.config_name.like(f"%{config_name}%"))
    if config_key:
        query = query.where(SysConfig.config_key.like(f"%{config_key}%"))
    if config_type:
        query = query.where(SysConfig.config_type == config_type)
    query = query.order_by(SysConfig.config_id)
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取参数配置列表成功")
    return ResponseUtil.success(model_content=result)


@configController.get("/configKey/{config_key}")
async def get_config_by_key(
    request: Request,
    config_key: str,
    query_db: AsyncSession = Depends(get_db),
):
    """根据参数键名获取参数值"""
    query = select(SysConfig).where(SysConfig.config_key == config_key)
    result = await query_db.execute(query)
    config = result.scalar()
    if config:
        logger.info("获取参数配置成功")
        return ResponseUtil.success(msg=config.config_value)
    return ResponseUtil.success(msg="")


@configController.get("/{config_id}")
async def get_config_detail(
    request: Request,
    config_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取参数配置详情"""
    query = select(SysConfig).where(SysConfig.config_id == config_id)
    result = await query_db.execute(query)
    config = result.scalar()
    logger.info("获取参数配置详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(config))


@configController.post("")
@Log(title="参数管理", business_type=1)
async def add_config(
    request: Request,
    config_data: ConfigEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增参数配置"""
    config = SysConfig(
        config_name=config_data.config_name,
        config_key=config_data.config_key,
        config_value=config_data.config_value,
        config_type=config_data.config_type or "N",
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
        remark=config_data.remark,
    )
    query_db.add(config)
    await query_db.commit()
    logger.info("新增参数配置成功")
    return ResponseUtil.success(msg="新增成功")


@configController.put("")
@Log(title="参数管理", business_type=2)
async def update_config(
    request: Request,
    config_data: ConfigEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改参数配置"""
    update_data = {
        "config_name": config_data.config_name,
        "config_key": config_data.config_key,
        "config_value": config_data.config_value,
        "config_type": config_data.config_type,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
        "remark": config_data.remark,
    }
    query = update(SysConfig).where(SysConfig.config_id == config_data.config_id).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改参数配置成功")
    return ResponseUtil.success(msg="修改成功")


@configController.delete("/refreshCache")
@Log(title="参数管理", business_type=9)
async def refresh_config_cache(
    request: Request,
):
    """刷新参数配置缓存"""
    await RedisUtil.init_sys_config(request.app.state.redis)
    logger.info("刷新参数配置缓存成功")
    return ResponseUtil.success(msg="刷新成功")


@configController.delete("/{config_ids}")
@Log(title="参数管理", business_type=3)
async def delete_config(
    request: Request,
    config_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除参数配置"""
    ids = config_ids.split(",")
    for cid in ids:
        query = delete(SysConfig).where(SysConfig.config_id == int(cid))
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除参数配置成功")
    return ResponseUtil.success(msg="删除成功")


@configController.post("/export")
@Log(title="参数管理", business_type=5)
async def export_config(
    request: Request,
    config_name: Optional[str] = Form(default=None, alias="configName"),
    config_key: Optional[str] = Form(default=None, alias="configKey"),
    config_type: Optional[str] = Form(default=None, alias="configType"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导出参数配置"""
    query = select(SysConfig)
    if config_name:
        query = query.where(SysConfig.config_name.like(f"%{config_name}%"))
    if config_key:
        query = query.where(SysConfig.config_key.like(f"%{config_key}%"))
    if config_type:
        query = query.where(SysConfig.config_type == config_type)

    query = query.order_by(SysConfig.config_id)
    result = await query_db.execute(query)
    configs = result.scalars().all()

    data = []
    for config in configs:
        data.append(
            {
                "参数主键": config.config_id,
                "参数名称": config.config_name,
                "参数键名": config.config_key,
                "参数键值": config.config_value,
                "系统内置": "是" if config.config_type == "Y" else "否",
                "备注": config.remark,
                "创建时间": config.create_time.strftime("%Y-%m-%d %H:%M:%S") if config.create_time else "",
            }
        )

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="参数配置")

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=config_list.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
