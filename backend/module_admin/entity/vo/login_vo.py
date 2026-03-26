from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class UserLogin(BaseModel):
    """用户登录模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    user_name: str = Field(description="用户名")
    password: str = Field(description="密码")
    code: Optional[str] = Field(default="", description="验证码")
    uuid: Optional[str] = Field(default="", description="验证码唯一标识")
    login_info: Optional[Dict[str, str]] = Field(default=None, description="登录信息")
    captcha_enabled: bool = Field(default=True, description="是否开启验证码")


class UserRegister(BaseModel):
    """用户注册模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    confirm_password: str = Field(description="确认密码")
    code: Optional[str] = Field(default="", description="验证码")
    uuid: Optional[str] = Field(default="", description="验证码唯一标识")


class Token(BaseModel):
    """Token模型"""

    access_token: str = Field(description="访问令牌")
    token_type: str = Field(default="Bearer", description="令牌类型")


class MenuTreeModel(BaseModel):
    """菜单树模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    menu_id: Optional[int] = Field(default=None, description="菜单ID")
    menu_name: Optional[str] = Field(default=None, description="菜单名称")
    parent_id: Optional[int] = Field(default=None, description="父菜单ID")
    order_num: Optional[int] = Field(default=None, description="显示顺序")
    path: Optional[str] = Field(default=None, description="路由地址")
    component: Optional[str] = Field(default=None, description="组件路径")
    query: Optional[str] = Field(default=None, description="路由参数")
    is_frame: Optional[int] = Field(default=None, description="是否为外链")
    is_cache: Optional[int] = Field(default=None, description="是否缓存")
    menu_type: Optional[str] = Field(default=None, description="菜单类型")
    visible: Optional[str] = Field(default=None, description="菜单状态")
    status: Optional[str] = Field(default=None, description="菜单状态")
    perms: Optional[str] = Field(default=None, description="权限标识")
    icon: Optional[str] = Field(default=None, description="菜单图标")
    children: Optional[List["MenuTreeModel"]] = Field(default=[], description="子菜单")


class MetaModel(BaseModel):
    """路由元信息模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    title: Optional[str] = Field(default=None, description="标题")
    icon: Optional[str] = Field(default=None, description="图标")
    no_cache: Optional[bool] = Field(default=False, alias="noCache", description="是否缓存")
    link: Optional[str] = Field(default=None, description="链接")


class RouterModel(BaseModel):
    """路由模型"""

    model_config = ConfigDict(alias_generator=to_camel)

    name: Optional[str] = Field(default=None, description="路由名称")
    path: Optional[str] = Field(default=None, description="路由地址")
    hidden: Optional[bool] = Field(default=False, description="是否隐藏")
    redirect: Optional[str] = Field(default=None, description="重定向地址")
    component: Optional[str] = Field(default=None, description="组件路径")
    query: Optional[str] = Field(default=None, description="路由参数")
    always_show: Optional[bool] = Field(default=None, alias="alwaysShow", description="是否总是显示")
    meta: Optional[MetaModel] = Field(default=None, description="路由元信息")
    children: Optional[List["RouterModel"]] = Field(default=[], description="子路由")


class SmsCode(BaseModel):
    """短信验证码模型"""

    is_success: bool = Field(description="是否成功")
    sms_code: str = Field(description="验证码")
    session_id: str = Field(description="会话ID")
    message: str = Field(description="消息")
