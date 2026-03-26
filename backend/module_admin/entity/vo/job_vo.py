from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class JobModel(BaseModel):
    """定时任务模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    job_id: Optional[int] = Field(default=None, description="任务ID")
    job_name: Optional[str] = Field(default=None, description="任务名称")
    job_group: Optional[str] = Field(default=None, description="任务组名")
    job_executor: Optional[str] = Field(default=None, description="任务执行器")
    invoke_target: Optional[str] = Field(default=None, description="调用目标字符串")
    job_args: Optional[str] = Field(default=None, description="位置参数")
    job_kwargs: Optional[str] = Field(default=None, description="关键字参数")
    cron_expression: Optional[str] = Field(default=None, description="cron执行表达式")
    misfire_policy: Optional[Literal["1", "2", "3"]] = Field(
        default=None, description="计划执行错误策略（1立即执行 2执行一次 3放弃执行）"
    )
    concurrent: Optional[Literal["0", "1"]] = Field(default=None, description="是否并发执行（0允许 1禁止）")
    status: Optional[Literal["0", "1"]] = Field(default=None, description="状态（0正常 1暂停）")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注信息")
    next_valid_time: Optional[datetime] = Field(default=None, description="下次执行时间")


class JobLogModel(BaseModel):
    """定时任务日志模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    job_log_id: Optional[int] = Field(default=None, description="任务日志ID")
    job_name: Optional[str] = Field(default=None, description="任务名称")
    job_group: Optional[str] = Field(default=None, description="任务组名")
    job_executor: Optional[str] = Field(default=None, description="任务执行器")
    invoke_target: Optional[str] = Field(default=None, description="调用目标字符串")
    job_args: Optional[str] = Field(default=None, description="位置参数")
    job_kwargs: Optional[str] = Field(default=None, description="关键字参数")
    job_trigger: Optional[str] = Field(default=None, description="任务触发器")
    job_message: Optional[str] = Field(default=None, description="日志信息")
    status: Optional[Literal["0", "1"]] = Field(default=None, description="执行状态（0正常 1失败）")
    exception_info: Optional[str] = Field(default=None, description="异常信息")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")


class JobQueryModel(JobModel):
    """定时任务查询模型"""

    begin_time: Optional[str] = Field(default=None, description="开始时间")
    end_time: Optional[str] = Field(default=None, description="结束时间")
    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")


class JobLogQueryModel(JobLogModel):
    """定时任务日志查询模型"""

    begin_time: Optional[str] = Field(default=None, description="开始时间")
    end_time: Optional[str] = Field(default=None, description="结束时间")
    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")


class EditJobModel(JobModel):
    """编辑定时任务模型"""

    type: Optional[str] = Field(default=None, description="操作类型")


class DeleteJobModel(BaseModel):
    """删除定时任务模型"""

    job_ids: str = Field(alias="jobIds", description="任务ID串")


class DeleteJobLogModel(BaseModel):
    """删除定时任务日志模型"""

    job_log_ids: str = Field(alias="jobLogIds", description="任务日志ID串")
