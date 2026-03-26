from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CrudResponseModel(BaseModel):
    """增删改查响应模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    is_success: bool = Field(default=True, description="是否成功")
    message: str = Field(default="操作成功", description="消息")
