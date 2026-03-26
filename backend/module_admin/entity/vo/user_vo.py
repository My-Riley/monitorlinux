from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TokenData(BaseModel):
    """token解析结果"""

    user_id: Union[int, None] = Field(default=None, description="用户ID")


class UserModel(BaseModel):
    """用户表对应pydantic模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    user_id: Optional[int] = Field(default=None, description="用户ID")
    dept_id: Optional[int] = Field(default=None, description="部门ID")
    user_name: Optional[str] = Field(default=None, description="用户账号")
    nick_name: Optional[str] = Field(default=None, description="用户昵称")
    user_type: Optional[str] = Field(default=None, description="用户类型")
    email: Optional[str] = Field(default=None, description="用户邮箱")
    phonenumber: Optional[str] = Field(default=None, description="手机号码")
    sex: Optional[Literal["0", "1", "2"]] = Field(default=None, description="用户性别")
    avatar: Optional[str] = Field(default=None, description="头像地址")
    password: Optional[str] = Field(default=None, description="密码")
    status: Optional[Literal["0", "1"]] = Field(default=None, description="帐号状态")
    del_flag: Optional[Literal["0", "2"]] = Field(default=None, description="删除标志")
    login_ip: Optional[str] = Field(default=None, description="最后登录IP")
    login_date: Optional[datetime] = Field(default=None, description="最后登录时间")
    pwd_update_date: Optional[datetime] = Field(default=None, description="密码最后更新时间")
    create_by: Optional[str] = Field(default=None, description="创建者")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_by: Optional[str] = Field(default=None, description="更新者")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")
    admin: Optional[bool] = Field(default=False, description="是否为admin")


class DeptModel(BaseModel):
    """部门模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    dept_id: Optional[int] = Field(default=None, description="部门ID")
    parent_id: Optional[int] = Field(default=None, description="父部门ID")
    ancestors: Optional[str] = Field(default=None, description="祖级列表")
    dept_name: Optional[str] = Field(default=None, description="部门名称")
    order_num: Optional[int] = Field(default=None, description="显示顺序")
    leader: Optional[str] = Field(default=None, description="负责人")
    phone: Optional[str] = Field(default=None, description="联系电话")
    email: Optional[str] = Field(default=None, description="邮箱")
    status: Optional[str] = Field(default=None, description="部门状态")


class RoleModel(BaseModel):
    """角色模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    role_id: Optional[int] = Field(default=None, description="角色ID")
    role_name: Optional[str] = Field(default=None, description="角色名称")
    role_key: Optional[str] = Field(default=None, description="角色权限字符串")
    role_sort: Optional[int] = Field(default=None, description="显示顺序")
    data_scope: Optional[str] = Field(default=None, description="数据范围")
    status: Optional[str] = Field(default=None, description="角色状态")


class UserInfoModel(UserModel):
    post_ids: Optional[Union[str, None]] = Field(default=None, description="岗位ID信息")
    role_ids: Optional[Union[str, None]] = Field(default=None, description="角色ID信息")
    dept: Optional[Union[DeptModel, None]] = Field(default=None, description="部门信息")
    role: Optional[List[Union[RoleModel, None]]] = Field(default=[], description="角色信息")


class CurrentUserModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    permissions: List = Field(description="权限信息")
    roles: List = Field(description="角色信息")
    user: Union[UserInfoModel, None] = Field(description="用户信息")
    is_default_modify_pwd: bool = Field(default=False, description="是否初始密码修改提醒")
    is_password_expired: bool = Field(default=False, description="密码是否过期提醒")


class EditUserModel(UserModel):
    """编辑用户模型"""

    role_ids: Optional[List[int]] = Field(default=[], description="角色ID信息")
    post_ids: Optional[List[int]] = Field(default=[], description="岗位ID信息")
    role: Optional[List] = Field(default=[], description="角色信息")
    type: Optional[str] = Field(default=None, description="操作类型")
