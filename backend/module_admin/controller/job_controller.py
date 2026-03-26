from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.job_vo import DeleteJobModel, EditJobModel, JobModel, JobQueryModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.job_service import JobService
from module_admin.service.login_service import LoginService
from utils.response_util import ResponseUtil

jobController = APIRouter(prefix="/monitor/job", tags=["定时任务"])


@jobController.get("/list", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:list"))])
async def get_job_list(
    request: Request,
    job_name: Optional[str] = Query(default=None, alias="jobName"),
    job_group: Optional[str] = Query(default=None, alias="jobGroup"),
    status: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取定时任务列表"""
    query_params = JobQueryModel(
        jobName=job_name, jobGroup=job_group, status=status, pageNum=page_num, pageSize=page_size
    )
    result = await JobService.get_job_list_services(query_db, query_params, is_page=True)
    return ResponseUtil.success(model_content=result)


@jobController.get("/{job_id}", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:query"))])
async def get_job_detail(
    request: Request,
    job_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取定时任务详情"""
    result = await JobService.job_detail_services(query_db, job_id)
    return ResponseUtil.success(data=result)


@jobController.post("", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:add"))])
@Log(title="定时任务", business_type=1)
async def add_job(
    request: Request,
    job: JobModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增定时任务"""
    job.create_by = current_user.user.user_name
    job.update_by = current_user.user.user_name
    result = await JobService.add_job_services(query_db, job)
    return ResponseUtil.success(msg=result.message)


@jobController.put("", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:edit"))])
@Log(title="定时任务", business_type=2)
async def update_job(
    request: Request,
    job: EditJobModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改定时任务"""
    job.update_by = current_user.user.user_name
    result = await JobService.edit_job_services(query_db, job)
    return ResponseUtil.success(msg=result.message)


@jobController.delete("/{job_ids}", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:remove"))])
@Log(title="定时任务", business_type=3)
async def delete_job(
    request: Request,
    job_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除定时任务"""
    result = await JobService.delete_job_services(query_db, DeleteJobModel(jobIds=job_ids))
    return ResponseUtil.success(msg=result.message)


@jobController.put("/changeStatus", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:changeStatus"))])
@Log(title="定时任务", business_type=2)
async def change_job_status(
    request: Request,
    job: EditJobModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改定时任务状态"""
    job.update_by = current_user.user.user_name
    job.type = "status"
    result = await JobService.edit_job_services(query_db, job)
    return ResponseUtil.success(msg=result.message)


@jobController.put("/run", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:changeStatus"))])
@Log(title="定时任务", business_type=2)
async def run_job(
    request: Request,
    job: JobModel,
    query_db: AsyncSession = Depends(get_db),
):
    """立即执行定时任务"""
    result = await JobService.execute_job_once_services(query_db, job)
    return ResponseUtil.success(msg=result.message)


@jobController.post("/export", dependencies=[Depends(CheckUserInterfaceAuth("monitor:job:export"))])
@Log(title="定时任务", business_type=5)
async def export_job(
    request: Request,
    job_name: Optional[str] = Query(default=None, alias="jobName"),
    job_group: Optional[str] = Query(default=None, alias="jobGroup"),
    status: Optional[str] = Query(default=None),
    query_db: AsyncSession = Depends(get_db),
):
    """导出定时任务"""
    query_params = JobQueryModel(
        jobName=job_name,
        jobGroup=job_group,
        status=status,
    )
    # 不分页获取全部
    job_list_result = await JobService.get_job_list_services(query_db, query_params, is_page=False)

    # 导出
    data = await JobService.export_job_list_services(request, job_list_result)
    return ResponseUtil.streaming(data=data)
