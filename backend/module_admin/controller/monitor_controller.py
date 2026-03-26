import io
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.enums import RedisInitKeyConfig
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.entity.do.log_do import SysLogininfor, SysOperLog
from module_admin.service.login_service import LoginService
from utils.log_util import logger
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil

operlogController = APIRouter(prefix="/monitor/operlog", dependencies=[Depends(LoginService.get_current_user)])
logininforController = APIRouter(prefix="/monitor/logininfor", dependencies=[Depends(LoginService.get_current_user)])


# 操作日志接口
@operlogController.get("/list")
async def get_operlog_list(
    request: Request,
    title: Optional[str] = Query(default=None),
    oper_ip: Optional[str] = Query(default=None, alias="operIp"),
    oper_name: Optional[str] = Query(default=None, alias="operName"),
    business_type: Optional[int] = Query(default=None, alias="businessType"),
    status: Optional[int] = Query(default=None),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取操作日志列表"""
    query = select(SysOperLog)
    if title:
        query = query.where(SysOperLog.title.like(f"%{title}%"))
    if oper_ip:
        query = query.where(SysOperLog.oper_ip.like(f"%{oper_ip}%"))
    if oper_name:
        query = query.where(SysOperLog.oper_name.like(f"%{oper_name}%"))
    if business_type is not None:
        query = query.where(SysOperLog.business_type == business_type)
    if status is not None:
        query = query.where(SysOperLog.status == status)
    if begin_time:
        query = query.where(SysOperLog.oper_time >= datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
    if end_time:
        query = query.where(SysOperLog.oper_time <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
    query = query.order_by(SysOperLog.oper_id.desc())
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取操作日志列表成功")
    return ResponseUtil.success(model_content=result)


@operlogController.post("/export")
@Log(title="操作日志", business_type=5)
async def export_operlog(
    request: Request,
    title: Optional[str] = Form(None),
    oper_name: Optional[str] = Form(None, alias="operName"),
    business_type: Optional[int] = Form(None, alias="businessType"),
    status: Optional[int] = Form(None),
    begin_time: Optional[str] = Form(None, alias="beginTime"),
    end_time: Optional[str] = Form(None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """导出操作日志"""
    query = select(SysOperLog)
    if title:
        query = query.where(SysOperLog.title.like(f"%{title}%"))
    if oper_name:
        query = query.where(SysOperLog.oper_name.like(f"%{oper_name}%"))
    if business_type is not None:
        query = query.where(SysOperLog.business_type == business_type)
    if status is not None:
        query = query.where(SysOperLog.status == status)
    if begin_time:
        query = query.where(SysOperLog.oper_time >= datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
    if end_time:
        query = query.where(SysOperLog.oper_time <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
    query = query.order_by(SysOperLog.oper_id.desc())

    result = await query_db.execute(query)
    rows = result.scalars().all()

    data = []
    for row in rows:
        data.append(
            {
                "日志编号": row.oper_id,
                "系统模块": row.title,
                "操作类型": row.business_type,
                "操作人员": row.oper_name,
                "操作地址": row.oper_ip,
                "操作地点": row.oper_location,
                "操作状态": "正常" if row.status == 0 else "失败",
                "操作时间": row.oper_time,
                "消耗时间": f"{row.cost_time}毫秒",
            }
        )
    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    headers = {"Content-Disposition": 'attachment; filename="operlog.xlsx"'}
    return StreamingResponse(
        output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@operlogController.delete("/clean")
@Log(title="操作日志", business_type=9)
async def clean_operlog(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """清空操作日志"""
    query = delete(SysOperLog)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("清空操作日志成功")
    return ResponseUtil.success(msg="清空成功")


@operlogController.delete("/{oper_ids}")
@Log(title="操作日志", business_type=3)
async def delete_operlog(
    request: Request,
    oper_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除操作日志"""
    ids = oper_ids.split(",")
    for oid in ids:
        query = delete(SysOperLog).where(SysOperLog.oper_id == int(oid))
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除操作日志成功")
    return ResponseUtil.success(msg="删除成功")


# 登录日志接口
@logininforController.get("/list")
async def get_logininfor_list(
    request: Request,
    user_name: Optional[str] = Query(default=None, alias="userName"),
    ipaddr: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取登录日志列表"""
    query = select(SysLogininfor)
    if user_name:
        query = query.where(SysLogininfor.user_name.like(f"%{user_name}%"))
    if ipaddr:
        query = query.where(SysLogininfor.ipaddr.like(f"%{ipaddr}%"))
    if status:
        query = query.where(SysLogininfor.status == status)
    if begin_time:
        query = query.where(SysLogininfor.login_time >= datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
    if end_time:
        query = query.where(SysLogininfor.login_time <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
    query = query.order_by(SysLogininfor.info_id.desc())
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取登录日志列表成功")
    return ResponseUtil.success(model_content=result)


@logininforController.post("/export")
@Log(title="登录日志", business_type=5)
async def export_logininfor(
    request: Request,
    user_name: Optional[str] = Form(None, alias="userName"),
    ipaddr: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    begin_time: Optional[str] = Form(None, alias="beginTime"),
    end_time: Optional[str] = Form(None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """导出登录日志"""
    query = select(SysLogininfor)
    if user_name:
        query = query.where(SysLogininfor.user_name.like(f"%{user_name}%"))
    if ipaddr:
        query = query.where(SysLogininfor.ipaddr.like(f"%{ipaddr}%"))
    if status:
        query = query.where(SysLogininfor.status == status)
    if begin_time:
        query = query.where(SysLogininfor.login_time >= datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
    if end_time:
        query = query.where(SysLogininfor.login_time <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
    query = query.order_by(SysLogininfor.info_id.desc())

    result = await query_db.execute(query)
    rows = result.scalars().all()

    data = []
    for row in rows:
        data.append(
            {
                "访问编号": row.info_id,
                "用户名称": row.user_name,
                "登录地址": row.ipaddr,
                "登录地点": row.login_location,
                "浏览器": row.browser,
                "操作系统": row.os,
                "登录状态": "成功" if row.status == "0" else "失败",
                "操作信息": row.msg,
                "登录日期": row.login_time,
            }
        )
    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    headers = {"Content-Disposition": 'attachment; filename="logininfor.xlsx"'}
    return StreamingResponse(
        output, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@logininforController.delete("/clean")
@Log(title="登录日志", business_type=9)
async def clean_logininfor(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """清空登录日志"""
    query = delete(SysLogininfor)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("清空登录日志成功")
    return ResponseUtil.success(msg="清空成功")


@logininforController.delete("/{info_ids}")
@Log(title="登录日志", business_type=3)
async def delete_logininfor(
    request: Request,
    info_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除登录日志"""
    ids = info_ids.split(",")
    for iid in ids:
        query = delete(SysLogininfor).where(SysLogininfor.info_id == int(iid))
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除登录日志成功")
    return ResponseUtil.success(msg="删除成功")


@logininforController.get("/unlock/{user_name}")
@Log(title="账户解锁", business_type=0)
async def unlock_logininfor(
    request: Request,
    user_name: str,
):
    """解锁用户登录状态"""
    # 清除Redis中的锁定状态（密码错误次数）
    redis_key = f"{RedisInitKeyConfig.PASSWORD_ERROR_COUNT.key}:{user_name}"
    await request.app.state.redis.delete(redis_key)
    logger.info(f"解锁用户 {user_name} 成功")
    return ResponseUtil.success(msg="解锁成功")
