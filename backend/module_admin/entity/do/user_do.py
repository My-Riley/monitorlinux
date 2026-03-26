from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from config.database import Base


class SysUser(Base):
    """用户信息表"""

    __tablename__ = "sys_user"
    __table_args__ = {"comment": "用户信息表"}

    user_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="用户ID")
    dept_id = Column(BigInteger, ForeignKey("sys_dept.dept_id"), nullable=True, comment="部门ID")
    user_name = Column(String(30), nullable=False, comment="用户账号")
    nick_name = Column(String(30), nullable=False, comment="用户昵称")
    user_type = Column(String(2), nullable=True, server_default="00", comment="用户类型")
    email = Column(String(50), nullable=True, server_default="", comment="用户邮箱")
    phonenumber = Column(String(11), nullable=True, server_default="", comment="手机号码")
    sex = Column(CHAR(1), nullable=True, server_default="0", comment="用户性别")
    avatar = Column(String(100), nullable=True, server_default="", comment="头像地址")
    password = Column(String(100), nullable=True, server_default="", comment="密码")
    status = Column(CHAR(1), nullable=True, server_default="0", comment="帐号状态")
    del_flag = Column(CHAR(1), nullable=True, server_default="0", comment="删除标志")
    login_ip = Column(String(128), nullable=True, server_default="", comment="最后登录IP")
    login_date = Column(DateTime, nullable=True, comment="最后登录时间")
    pwd_update_date = Column(DateTime, nullable=True, comment="密码最后更新时间")
    create_by = Column(String(64), nullable=True, server_default="", comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, server_default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")

    dept = relationship("SysDept", backref="users", lazy="joined")


class SysUserRole(Base):
    """用户和角色关联表"""

    __tablename__ = "sys_user_role"
    __table_args__ = {"comment": "用户和角色关联表"}

    user_id = Column(BigInteger, primary_key=True, nullable=False, comment="用户ID")
    role_id = Column(BigInteger, primary_key=True, nullable=False, comment="角色ID")


class SysUserPost(Base):
    """用户与岗位关联表"""

    __tablename__ = "sys_user_post"
    __table_args__ = {"comment": "用户与岗位关联表"}

    user_id = Column(BigInteger, primary_key=True, nullable=False, comment="用户ID")
    post_id = Column(BigInteger, primary_key=True, nullable=False, comment="岗位ID")
