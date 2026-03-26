from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class WarnModel(BaseModel):
    """预警模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    warn_id: Optional[int] = Field(default=None, description="预警ID")
    warn_name: Optional[str] = Field(default=None, description="预警名称")
    warn_level: Optional[str] = Field(default=None, description="预警级别")
    warn_content: Optional[str] = Field(default=None, description="预警内容")
    warn_time: Optional[datetime] = Field(default=None, description="预警时间")
    camera_id: Optional[int] = Field(default=None, description="摄像头ID")
    camera_name: Optional[str] = Field(default=None, description="摄像头名称")
    status: Optional[str] = Field(default=None, description="状态")
    handle_result: Optional[str] = Field(default=None, description="处理结果")
    handle_time: Optional[datetime] = Field(default=None, description="处理时间")
    handle_by: Optional[str] = Field(default=None, description="处理人")
    remark: Optional[str] = Field(default=None, description="备注")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class WarnQueryModel(WarnModel):
    """预警查询模型"""

    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")
    begin_time: Optional[str] = Field(default=None, alias="beginTime", description="开始时间")
    end_time: Optional[str] = Field(default=None, alias="endTime", description="结束时间")
