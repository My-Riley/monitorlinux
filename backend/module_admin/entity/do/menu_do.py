from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String

from config.database import Base


class SysMenu(Base):
    """菜单权限表"""

    __tablename__ = "sys_menu"
    __table_args__ = {"comment": "菜单权限表"}

    menu_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="菜单ID")
    menu_name = Column(String(50), nullable=False, comment="菜单名称")
    parent_id = Column(BigInteger, nullable=True, server_default="0", comment="父菜单ID")
    order_num = Column(BigInteger, nullable=True, server_default="0", comment="显示顺序")
    path = Column(String(200), nullable=True, comment="路由地址")
    component = Column(String(255), nullable=True, comment="组件路径")
    query = Column(String(255), nullable=True, comment="路由参数")
    is_frame = Column(BigInteger, nullable=True, server_default="1", comment="是否为外链")
    is_cache = Column(BigInteger, nullable=True, server_default="0", comment="是否缓存")
    menu_type = Column(CHAR(1), nullable=True, comment="菜单类型")
    visible = Column(CHAR(1), nullable=True, server_default="0", comment="菜单状态")
    status = Column(CHAR(1), nullable=True, server_default="0", comment="菜单状态")
    perms = Column(String(100), nullable=True, comment="权限标识")
    icon = Column(String(100), nullable=True, server_default="#", comment="菜单图标")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")
