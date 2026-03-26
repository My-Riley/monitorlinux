from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class NoticeModel(BaseModel):
    """通知公告模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    notice_id: Optional[int] = Field(default=None, description="公告ID")
    notice_title: Optional[str] = Field(default=None, description="公告标题")
    notice_type: Optional[Literal["1", "2"]] = Field(default=None, description="公告类型（1通知 2公告）")
    notice_content: Optional[str] = Field(default=None, description="公告内容")
    status: Optional[Literal["0", "1"]] = Field(default=None, description="公告状态（0正常 1关闭）")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


class NoticeQueryModel(NoticeModel):
    """通知公告查询模型"""

    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")
    begin_time: Optional[str] = Field(default=None, alias="beginTime", description="开始时间")
    end_time: Optional[str] = Field(default=None, alias="endTime", description="结束时间")
