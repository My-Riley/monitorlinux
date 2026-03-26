from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String

from config.database import Base


class SysRole(Base):
    """角色信息表"""

    __tablename__ = "sys_role"
    __table_args__ = {"comment": "角色信息表"}

    role_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="角色ID")
    role_name = Column(String(30), nullable=False, comment="角色名称")
    role_key = Column(String(100), nullable=False, comment="角色权限字符串")
    role_sort = Column(BigInteger, nullable=False, comment="显示顺序")
    data_scope = Column(CHAR(1), nullable=True, server_default="1", comment="数据范围")
    menu_check_strictly = Column(BigInteger, nullable=True, server_default="1", comment="菜单树选择项是否关联显示")
    dept_check_strictly = Column(BigInteger, nullable=True, server_default="1", comment="部门树选择项是否关联显示")
    status = Column(CHAR(1), nullable=False, comment="角色状态")
    del_flag = Column(CHAR(1), nullable=True, server_default="0", comment="删除标志")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")


class SysRoleMenu(Base):
    """角色和菜单关联表"""

    __tablename__ = "sys_role_menu"
    __table_args__ = {"comment": "角色和菜单关联表"}

    role_id = Column(BigInteger, primary_key=True, nullable=False, comment="角色ID")
    menu_id = Column(BigInteger, primary_key=True, nullable=False, comment="菜单ID")


class SysRoleDept(Base):
    """角色和部门关联表"""

    __tablename__ = "sys_role_dept"
    __table_args__ = {"comment": "角色和部门关联表"}

    role_id = Column(BigInteger, primary_key=True, nullable=False, comment="角色ID")
    dept_id = Column(BigInteger, primary_key=True, nullable=False, comment="部门ID")
