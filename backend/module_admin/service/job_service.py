from typing import List

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.constant import CommonConstant
from config.get_scheduler import SchedulerUtil
from exceptions.exception import ServiceException
from module_admin.dao.job_dao import JobDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.job_vo import DeleteJobModel, EditJobModel, JobModel, JobQueryModel
from module_admin.service.dict_service import DictDataService
from utils.common_util import CamelCaseUtil
from utils.cron_util import CronUtil
from utils.excel_util import ExcelUtil
from utils.string_util import StringUtil


class JobService:
    """定时任务管理服务层"""

    @classmethod
    async def get_job_list_services(cls, query_db: AsyncSession, query_params: JobQueryModel, is_page: bool = False):
        """获取任务列表"""
        return await JobDao.get_job_list(query_db, query_params, is_page)

    @classmethod
    async def check_job_unique_services(cls, query_db: AsyncSession, job_model: JobModel):
        """校验任务是否唯一"""
        # TODO: 补全 JobDao.get_job_detail_by_info 以支持更严格的唯一性校验
        return CommonConstant.UNIQUE

    @classmethod
    async def add_job_services(cls, query_db: AsyncSession, job_model: JobModel):
        """新增任务"""
        if not CronUtil.validate_cron_expression(job_model.cron_expression):
            raise ServiceException(message=f"新增任务{job_model.job_name}失败，Cron表达式不正确")

        # 检查违规调用
        if StringUtil.contains_ignore_case(job_model.invoke_target, CommonConstant.LOOKUP_RMI):
            raise ServiceException(message=f"新增任务{job_model.job_name}失败，目标字符串不允许rmi调用")

        # 更多检查省略...

        from module_admin.entity.do.job_do import SysJob

        job = SysJob(**job_model.model_dump(exclude_unset=True))
        try:
            added_job = await JobDao.add_job(query_db, job)
            # 添加到调度器
            job_info = await cls.job_detail_services(query_db, added_job.job_id)
            if job_info.status == "0":
                SchedulerUtil.add_scheduler_job(job_info=job_info)
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_job_services(cls, query_db: AsyncSession, edit_job_model: EditJobModel):
        """编辑任务"""
        job_info = await cls.job_detail_services(query_db, edit_job_model.job_id)
        if not job_info.job_id:  # 检查是否存在
            raise ServiceException(message="任务不存在")

        # Check uniqueness
        check_model = JobModel(
            job_id=edit_job_model.job_id,
            job_name=edit_job_model.job_name or job_info.job_name,
            job_group=edit_job_model.job_group or job_info.job_group,
        )
        if await cls.check_job_unique_services(query_db, check_model) == CommonConstant.NOT_UNIQUE:
            raise ServiceException(message=f"编辑任务'{check_model.job_name}'失败，任务已存在")

        job_data = edit_job_model.model_dump(exclude_unset=True)
        if hasattr(edit_job_model, "type") and edit_job_model.type == "status":
            del job_data["type"]

        # 移除不在数据库表中的字段
        if "next_valid_time" in job_data:
            del job_data["next_valid_time"]

        try:
            await JobDao.update_job(query_db, edit_job_model.job_id, job_data)
            # 更新调度器
            SchedulerUtil.remove_scheduler_job(job_id=str(edit_job_model.job_id))
            # 获取最新信息
            new_job_info = await cls.job_detail_services(query_db, edit_job_model.job_id)
            if new_job_info.status == "0":
                SchedulerUtil.add_scheduler_job(job_info=new_job_info)

            return CrudResponseModel(is_success=True, message="更新成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def execute_job_once_services(cls, query_db: AsyncSession, job_model: JobModel):
        """执行一次"""
        job_info = await cls.job_detail_services(query_db, job_model.job_id)
        if job_info.job_id:
            SchedulerUtil.execute_scheduler_job_once(job_info=job_info)
            return CrudResponseModel(is_success=True, message="执行成功")
        raise ServiceException(message="任务不存在")

    @classmethod
    async def delete_job_services(cls, query_db: AsyncSession, delete_model: DeleteJobModel):
        """删除任务"""
        if delete_model.job_ids:
            job_ids = delete_model.job_ids.split(",")
            try:
                await JobDao.delete_job(query_db, job_ids)
                for job_id in job_ids:
                    SchedulerUtil.remove_scheduler_job(job_id=job_id)
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        raise ServiceException(message="传入ID为空")

    @classmethod
    async def job_detail_services(cls, query_db: AsyncSession, job_id: int):
        """获取任务详情"""
        job = await JobDao.get_job_detail_by_id(query_db, job_id)
        if job:
            job_model = JobModel(**CamelCaseUtil.transform_result(job))
            # 从调度器获取下次执行时间
            scheduler_job = SchedulerUtil.get_scheduler_job(job_id)
            if scheduler_job:
                job_model.next_valid_time = scheduler_job.next_run_time
            return job_model
        return JobModel()

    @classmethod
    async def export_job_list_services(cls, request: Request, job_list: List):
        """导出任务"""
        mapping_dict = {
            "jobId": "任务编码",
            "jobName": "任务名称",
            "jobGroup": "任务组名",
            "jobExecutor": "任务执行器",
            "invokeTarget": "调用目标字符串",
            "jobArgs": "位置参数",
            "jobKwargs": "关键字参数",
            "cronExpression": "cron执行表达式",
            "misfirePolicy": "计划执行错误策略",
            "concurrent": "是否并发执行",
            "status": "状态",
            "createBy": "创建者",
            "createTime": "创建时间",
            "remark": "备注",
        }

        # 获取字典数据
        job_group_list = await DictDataService.query_dict_data_list_from_cache_services(
            request.app.state.redis, dict_type="sys_job_group"
        )
        job_group_map = {item.get("dictValue"): item.get("dictLabel") for item in job_group_list}

        job_executor_list = await DictDataService.query_dict_data_list_from_cache_services(
            request.app.state.redis, dict_type="sys_job_executor"
        )
        job_executor_map = {item.get("dictValue"): item.get("dictLabel") for item in job_executor_list}

        export_list = []
        for item in job_list:
            data = item.__dict__ if hasattr(item, "__dict__") else item
            if not isinstance(data, dict):
                data = {c.name: getattr(item, c.name) for c in item.__table__.columns}

            new_data = {}
            new_data.update(data)
            # 驼峰转换
            new_data = CamelCaseUtil.transform_result(new_data)

            # 状态映射
            status_val = str(new_data.get("status"))
            new_data["status"] = "正常" if status_val == "0" else "暂停"

            # 字典映射 - 任务组名
            job_group_val = str(new_data.get("jobGroup"))
            if job_group_val in job_group_map:
                new_data["jobGroup"] = job_group_map[job_group_val]

            # 字典映射 - 任务执行器
            job_executor_val = str(new_data.get("jobExecutor"))
            if job_executor_val in job_executor_map:
                new_data["jobExecutor"] = job_executor_map[job_executor_val]

            export_list.append(new_data)

        return ExcelUtil.export_list2excel(export_list, mapping_dict)
