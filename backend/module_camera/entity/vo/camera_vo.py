from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CameraModel(BaseModel):
    """摄像头模型 - 对应 sys_camera 表"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    camera_id: Optional[int] = Field(default=None, description="摄像头ID")
    camera_name: Optional[str] = Field(default=None, description="摄像头名称")
    region_id: Optional[int] = Field(default=None, description="区域ID")
    status: Optional[str] = Field(default=None, description="状态")
    del_flag: Optional[str] = Field(default=None, description="删除标志")
    username: Optional[str] = Field(default=None, description="登录用户名")
    password: Optional[str] = Field(default=None, description="登录密码")
    ip_addr: Optional[str] = Field(default=None, description="IP地址")
    port: Optional[str] = Field(default=None, description="端口")
    rtsp_port: Optional[str] = Field(default=None, description="RTSP端口")
    protocol: Optional[str] = Field(default=None, description="协议")
    brand: Optional[str] = Field(default=None, description="品牌")
    line: Optional[str] = Field(default=None, description="线路")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


class CameraQueryModel(CameraModel):
    """摄像头查询模型"""

    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")
