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
from module_admin.entity.do.dict_do import SysDictData, SysDictType
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil

dictTypeController = APIRouter(prefix="/system/dict/type", dependencies=[Depends(LoginService.get_current_user)])
dictDataController = APIRouter(prefix="/system/dict/data", dependencies=[Depends(LoginService.get_current_user)])


class DictTypeEditModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    dict_id: Optional[int] = Field(default=None)
    dict_name: Optional[str] = Field(default=None)
    dict_type: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)


class DictDataEditModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    dict_code: Optional[int] = Field(default=None)
    dict_sort: Optional[int] = Field(default=None)
    dict_label: Optional[str] = Field(default=None)
    dict_value: Optional[str] = Field(default=None)
    dict_type: Optional[str] = Field(default=None)
    css_class: Optional[str] = Field(default=None)
    list_class: Optional[str] = Field(default=None)
    is_default: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)


# 字典类型接口
@dictTypeController.get("/list")
async def get_dict_type_list(
    request: Request,
    dict_name: Optional[str] = Query(default=None, alias="dictName"),
    dict_type: Optional[str] = Query(default=None, alias="dictType"),
    status: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取字典类型列表"""
    query = select(SysDictType)
    if dict_name:
        query = query.where(SysDictType.dict_name.like(f"%{dict_name}%"))
    if dict_type:
        query = query.where(SysDictType.dict_type.like(f"%{dict_type}%"))
    if status:
        query = query.where(SysDictType.status == status)
    query = query.order_by(SysDictType.dict_id)
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取字典类型列表成功")
    return ResponseUtil.success(model_content=result)


@dictTypeController.get("/optionselect")
async def get_dict_type_option(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """获取字典类型选择框列表"""
    query = select(SysDictType).where(SysDictType.status == "0")
    result = await query_db.execute(query)
    types = result.scalars().all()
    logger.info("获取字典类型选择框列表成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(types))


@dictTypeController.get("/{dict_id}")
async def get_dict_type_detail(
    request: Request,
    dict_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取字典类型详情"""
    query = select(SysDictType).where(SysDictType.dict_id == dict_id)
    result = await query_db.execute(query)
    dict_type = result.scalar()
    logger.info("获取字典类型详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(dict_type))


@dictTypeController.post("")
@Log(title="字典类型", business_type=1)
async def add_dict_type(
    request: Request,
    dict_data: DictTypeEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增字典类型"""
    dict_type = SysDictType(
        dict_name=dict_data.dict_name,
        dict_type=dict_data.dict_type,
        status=dict_data.status or "0",
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
        remark=dict_data.remark,
    )
    query_db.add(dict_type)
    await query_db.commit()
    logger.info("新增字典类型成功")
    return ResponseUtil.success(msg="新增成功")


@dictTypeController.put("")
@Log(title="字典类型", business_type=2)
async def update_dict_type(
    request: Request,
    dict_data: DictTypeEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改字典类型"""
    update_data = {
        "dict_name": dict_data.dict_name,
        "dict_type": dict_data.dict_type,
        "status": dict_data.status,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
        "remark": dict_data.remark,
    }
    query = update(SysDictType).where(SysDictType.dict_id == dict_data.dict_id).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改字典类型成功")
    return ResponseUtil.success(msg="修改成功")


@dictTypeController.delete("/refreshCache")
@Log(title="字典类型", business_type=9)
async def refresh_dict_cache(
    request: Request,
):
    """刷新字典缓存"""
    await RedisUtil.init_sys_dict(request.app.state.redis)
    logger.info("刷新字典缓存成功")
    return ResponseUtil.success(msg="刷新成功")


@dictTypeController.delete("/{dict_ids}")
@Log(title="字典类型", business_type=3)
async def delete_dict_type(
    request: Request,
    dict_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除字典类型"""
    ids = dict_ids.split(",")
    for did in ids:
        query = delete(SysDictType).where(SysDictType.dict_id == int(did))
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除字典类型成功")
    return ResponseUtil.success(msg="删除成功")


@dictTypeController.post("/export")
@Log(title="字典类型", business_type=5)
async def export_dict_type(
    request: Request,
    dict_name: Optional[str] = Form(default=None, alias="dictName"),
    dict_type: Optional[str] = Form(default=None, alias="dictType"),
    status: Optional[str] = Form(default=None),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导出字典类型"""
    query = select(SysDictType)
    if dict_name:
        query = query.where(SysDictType.dict_name.like(f"%{dict_name}%"))
    if dict_type:
        query = query.where(SysDictType.dict_type.like(f"%{dict_type}%"))
    if status:
        query = query.where(SysDictType.status == status)

    query = query.order_by(SysDictType.dict_id)
    result = await query_db.execute(query)
    types = result.scalars().all()

    data = []
    for type_item in types:
        data.append(
            {
                "字典主键": type_item.dict_id,
                "字典名称": type_item.dict_name,
                "字典类型": type_item.dict_type,
                "状态": "正常" if type_item.status == "0" else "停用",
                "备注": type_item.remark,
                "创建时间": type_item.create_time.strftime("%Y-%m-%d %H:%M:%S") if type_item.create_time else "",
            }
        )

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="字典类型")

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=dict_type.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


# 字典数据接口
@dictDataController.get("/list")
async def get_dict_data_list(
    request: Request,
    dict_type: Optional[str] = Query(default=None, alias="dictType"),
    dict_label: Optional[str] = Query(default=None, alias="dictLabel"),
    status: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取字典数据列表"""
    query = select(SysDictData)
    if dict_type:
        query = query.where(SysDictData.dict_type == dict_type)
    if dict_label:
        query = query.where(SysDictData.dict_label.like(f"%{dict_label}%"))
    if status:
        query = query.where(SysDictData.status == status)
    query = query.order_by(SysDictData.dict_sort)
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取字典数据列表成功")
    return ResponseUtil.success(model_content=result)


@dictDataController.get("/type/{dict_type}")
async def get_dict_data_by_type(
    request: Request,
    dict_type: str,
    query_db: AsyncSession = Depends(get_db),
):
    """根据字典类型获取字典数据"""
    query = select(SysDictData).where(SysDictData.dict_type == dict_type, SysDictData.status == "0")
    query = query.order_by(SysDictData.dict_sort)
    result = await query_db.execute(query)
    data = result.scalars().all()
    logger.info("获取字典数据成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(data))


@dictDataController.get("/{dict_code}")
async def get_dict_data_detail(
    request: Request,
    dict_code: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取字典数据详情"""
    query = select(SysDictData).where(SysDictData.dict_code == dict_code)
    result = await query_db.execute(query)
    data = result.scalar()
    logger.info("获取字典数据详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(data))


@dictDataController.post("")
@Log(title="字典数据", business_type=1)
async def add_dict_data(
    request: Request,
    dict_data: DictDataEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增字典数据"""
    data = SysDictData(
        dict_sort=dict_data.dict_sort or 0,
        dict_label=dict_data.dict_label,
        dict_value=dict_data.dict_value,
        dict_type=dict_data.dict_type,
        css_class=dict_data.css_class,
        list_class=dict_data.list_class,
        is_default=dict_data.is_default or "N",
        status=dict_data.status or "0",
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
        remark=dict_data.remark,
    )
    query_db.add(data)
    await query_db.commit()
    logger.info("新增字典数据成功")
    return ResponseUtil.success(msg="新增成功")


@dictDataController.put("")
@Log(title="字典数据", business_type=2)
async def update_dict_data(
    request: Request,
    dict_data: DictDataEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改字典数据"""
    update_data = {
        "dict_sort": dict_data.dict_sort,
        "dict_label": dict_data.dict_label,
        "dict_value": dict_data.dict_value,
        "dict_type": dict_data.dict_type,
        "css_class": dict_data.css_class,
        "list_class": dict_data.list_class,
        "is_default": dict_data.is_default,
        "status": dict_data.status,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
        "remark": dict_data.remark,
    }
    query = update(SysDictData).where(SysDictData.dict_code == dict_data.dict_code).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改字典数据成功")
    return ResponseUtil.success(msg="修改成功")


@dictDataController.delete("/{dict_codes}")
@Log(title="字典数据", business_type=3)
async def delete_dict_data(
    request: Request,
    dict_codes: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除字典数据"""
    codes = dict_codes.split(",")
    for code in codes:
        query = delete(SysDictData).where(SysDictData.dict_code == int(code))
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除字典数据成功")
    return ResponseUtil.success(msg="删除成功")


@dictDataController.post("/export")
@Log(title="字典数据", business_type=5)
async def export_dict_data(
    request: Request,
    dict_type: Optional[str] = Form(default=None, alias="dictType"),
    dict_label: Optional[str] = Form(default=None, alias="dictLabel"),
    status: Optional[str] = Form(default=None),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导出字典数据"""
    query = select(SysDictData)
    if dict_type:
        query = query.where(SysDictData.dict_type == dict_type)
    if dict_label:
        query = query.where(SysDictData.dict_label.like(f"%{dict_label}%"))
    if status:
        query = query.where(SysDictData.status == status)

    query = query.order_by(SysDictData.dict_sort)
    result = await query_db.execute(query)
    data_list = result.scalars().all()

    data = []
    for item in data_list:
        data.append(
            {
                "字典编码": item.dict_code,
                "字典排序": item.dict_sort,
                "字典标签": item.dict_label,
                "字典键值": item.dict_value,
                "字典类型": item.dict_type,
                "状态": "正常" if item.status == "0" else "停用",
                "备注": item.remark,
                "创建时间": item.create_time.strftime("%Y-%m-%d %H:%M:%S") if item.create_time else "",
            }
        )

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="字典数据")

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=dict_data.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
