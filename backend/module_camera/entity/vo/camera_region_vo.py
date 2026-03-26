from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class RegionModel(BaseModel):
    """区域模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    region_id: Optional[int] = Field(default=None, description="区域ID")
    parent_id: Optional[int] = Field(default=0, description="父区域ID")
    ancestors: Optional[str] = Field(default=None, description="祖级列表")
    region_name: Optional[str] = Field(default=None, description="区域名称")
    order_num: Optional[int] = Field(default=0, description="显示顺序")
    address: Optional[str] = Field(default=None, description="地址")
    status: Optional[str] = Field(default="0", description="状态")
    del_flag: Optional[str] = Field(default="0", description="删除标志")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")


class RegionQueryModel(RegionModel):
    """区域查询模型"""

    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")
