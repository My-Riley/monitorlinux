from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class EmotionAnalysisResultModel(BaseModel):
    """情绪识别结果模型 - 对应 sys_emotion_result 表"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    result_id: Optional[int] = Field(default=None, description="结果ID")
    student_id: Optional[str] = Field(default=None, description="学号")
    student_name: Optional[str] = Field(default=None, description="学生姓名")
    emotion: Optional[str] = Field(default=None, description="情绪类型")
    camera_ip: Optional[str] = Field(default=None, description="摄像头IP")
    image_base64: Optional[str] = Field(default=None, description="Base64图片")
    image_path: Optional[str] = Field(default=None, description="图片路径")
    url: Optional[str] = Field(default=None, description="图片URL")
    statistics: Optional[str] = Field(default=None, description="统计")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")


class EmotionQueryModel(EmotionAnalysisResultModel):
    """情绪识别查询模型"""

    page_num: int = Field(default=1, alias="pageNum", description="当前页码")
    page_size: int = Field(default=10, alias="pageSize", description="每页记录数")
    begin_time: Optional[str] = Field(default=None, alias="beginTime", description="开始时间")
    end_time: Optional[str] = Field(default=None, alias="endTime", description="结束时间")
