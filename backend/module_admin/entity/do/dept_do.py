from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String

from config.database import Base


class SysDept(Base):
    """部门表"""

    __tablename__ = "sys_dept"
    __table_args__ = {"comment": "部门表"}

    dept_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="部门id")
    parent_id = Column(BigInteger, nullable=True, server_default="0", comment="父部门id")
    ancestors = Column(String(50), nullable=True, comment="祖级列表")
    dept_name = Column(String(30), nullable=True, comment="部门名称")
    order_num = Column(BigInteger, nullable=True, server_default="0", comment="显示顺序")
    leader = Column(String(20), nullable=True, comment="负责人")
    phone = Column(String(11), nullable=True, comment="联系电话")
    email = Column(String(50), nullable=True, comment="邮箱")
    status = Column(CHAR(1), nullable=True, server_default="0", comment="部门状态")
    del_flag = Column(CHAR(1), nullable=True, server_default="0", comment="删除标志")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间")
