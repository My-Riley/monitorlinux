from typing import List

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.dao.job_log_dao import JobLogDao
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.job_vo import DeleteJobLogModel, JobLogModel, JobLogQueryModel
from module_admin.service.dict_service import DictDataService
from utils.excel_util import ExcelUtil


class JobLogService:
    """定时任务日志管理服务层"""

    @classmethod
    async def get_job_log_list_services(
        cls, query_db: AsyncSession, query_params: JobLogQueryModel, is_page: bool = False
    ):
        """获取日志列表"""
        return await JobLogDao.get_job_log_list(query_db, query_params, is_page)

    @classmethod
    async def add_job_log_services(cls, query_db: AsyncSession, job_log: JobLogModel):
        """新增日志"""
        # 转换 DO 对象
        from module_admin.entity.do.job_do import SysJobLog

        db_job_log = SysJobLog(**job_log.model_dump(exclude_unset=True))
        try:
            await JobLogDao.add_job_log(query_db, db_job_log)
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_job_log_services(cls, query_db: AsyncSession, job_log_ids: DeleteJobLogModel):
        """删除日志"""
        if job_log_ids.job_log_ids:
            id_list = job_log_ids.job_log_ids.split(",")
            try:
                await JobLogDao.delete_job_log(query_db, id_list)
                return CrudResponseModel(is_success=True, message="删除成功")
            except Exception as e:
                await query_db.rollback()
                raise e
        raise ServiceException(message="传入ID为空")

    @classmethod
    async def clear_job_log_services(cls, query_db: AsyncSession):
        """清空日志"""
        try:
            await JobLogDao.clear_job_log(query_db)
            return CrudResponseModel(is_success=True, message="清除成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def export_job_log_list_services(cls, request: Request, job_log_list: List):
        """导出日志"""
        mapping_dict = {
            "jobLogId": "任务日志编码",
            "jobName": "任务名称",
            "jobGroup": "任务组名",
            "jobExecutor": "任务执行器",
            "invokeTarget": "调用目标字符串",
            "jobArgs": "位置参数",
            "jobKwargs": "关键字参数",
            "jobTrigger": "任务触发器",
            "jobMessage": "日志信息",
            "status": "执行状态",
            "exceptionInfo": "异常信息",
            "createTime": "创建时间",
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
        for item in job_log_list:
            # 转换为字典以便处理
            data = item.__dict__ if hasattr(item, "__dict__") else item
            # 处理 SysJobLog 对象
            if not isinstance(data, dict):
                # SQLAlchemy object to dict
                data = {c.name: getattr(item, c.name) for c in item.__table__.columns}

            new_data = {}
            # Use camelCase keys because PageUtil.paginate(is_page=False) returns camelCase transformed data
            new_data["jobLogId"] = data.get("jobLogId")
            new_data["jobName"] = data.get("jobName")
            new_data["invokeTarget"] = data.get("invokeTarget")
            new_data["jobArgs"] = data.get("jobArgs")
            new_data["jobKwargs"] = data.get("jobKwargs")
            new_data["jobTrigger"] = data.get("jobTrigger")
            new_data["jobMessage"] = data.get("jobMessage")
            new_data["exceptionInfo"] = data.get("exceptionInfo")
            new_data["createTime"] = data.get("createTime")

            # 状态映射
            status_val = data.get("status")
            new_data["status"] = "正常" if str(status_val) == "0" else "失败"

            # 字典映射 - 任务组名
            job_group_val = data.get("jobGroup")
            if str(job_group_val) in job_group_map:
                new_data["jobGroup"] = job_group_map[str(job_group_val)]
            else:
                new_data["jobGroup"] = job_group_val

            # 字典映射 - 任务执行器
            job_executor_val = data.get("jobExecutor")
            if str(job_executor_val) in job_executor_map:
                new_data["jobExecutor"] = job_executor_map[str(job_executor_val)]
            else:
                new_data["jobExecutor"] = job_executor_val

            export_list.append(new_data)

        return ExcelUtil.export_list2excel(export_list, mapping_dict)
