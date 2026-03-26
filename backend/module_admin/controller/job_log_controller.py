from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.job_vo import DeleteJobLogModel, JobLogQueryModel
from module_admin.service.job_log_service import JobLogService
from utils.response_util import ResponseUtil

jobLogController = APIRouter(prefix="/monitor/jobLog", tags=["定时任务日志"])


@jobLogController.get("/list", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:list"))])
async def get_job_log_list(
    request: Request,
    job_name: Optional[str] = Query(default=None, alias="jobName"),
    job_group: Optional[str] = Query(default=None, alias="jobGroup"),
    status: Optional[str] = Query(default=None),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取定时任务日志列表"""
    query_params = JobLogQueryModel(
        jobName=job_name,
        jobGroup=job_group,
        status=status,
        beginTime=begin_time,
        endTime=end_time,
        pageNum=page_num,
        pageSize=page_size,
    )
    result = await JobLogService.get_job_log_list_services(query_db, query_params, is_page=True)
    return ResponseUtil.success(model_content=result)


@jobLogController.delete("/clean", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:remove"))])
@Log(title="定时任务日志", business_type=9)
async def clean_job_log(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
):
    """清空定时任务日志"""
    result = await JobLogService.clear_job_log_services(query_db)
    return ResponseUtil.success(msg=result.message)


@jobLogController.delete("/{job_log_ids}", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:remove"))])
@Log(title="定时任务日志", business_type=3)
async def delete_job_log(
    request: Request,
    job_log_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除定时任务日志"""
    result = await JobLogService.delete_job_log_services(query_db, DeleteJobLogModel(jobLogIds=job_log_ids))
    return ResponseUtil.success(msg=result.message)


@jobLogController.post("/export", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:export"))])
@Log(title="定时任务日志", business_type=5)
async def export_job_log(
    request: Request,
    job_name: Optional[str] = Query(default=None, alias="jobName"),
    job_group: Optional[str] = Query(default=None, alias="jobGroup"),
    status: Optional[str] = Query(default=None),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """导出定时任务日志"""
    query_params = JobLogQueryModel(
        jobName=job_name,
        jobGroup=job_group,
        status=status,
        beginTime=begin_time,
        endTime=end_time,
    )
    # 不分页获取全部
    job_log_list_result = await JobLogService.get_job_log_list_services(query_db, query_params, is_page=False)

    # 导出
    data = await JobLogService.export_job_log_list_services(request, job_log_list_result)
    return ResponseUtil.streaming(data=data)
