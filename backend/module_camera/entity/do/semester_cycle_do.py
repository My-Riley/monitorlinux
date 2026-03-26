from datetime import datetime

from sqlalchemy import CHAR, Column, Date, DateTime, Integer, String

from config.database import Base


class SysSemesterCycle(Base):
    __tablename__ = "sys_semester_cycle"
    __table_args__ = {"comment": "学期周期表"}

    cycle_id = Column(Integer, primary_key=True, autoincrement=True, comment="周期ID")
    semester_id = Column(String(32), nullable=False, comment="学期ID")
    week_num = Column(Integer, nullable=False, comment="周次")
    name = Column(String(128), nullable=False, default="", comment="周期名称")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    status = Column(CHAR(1), nullable=False, default="0", comment="状态(0正常 1停用)")
    order_num = Column(Integer, nullable=False, default=0, comment="排序")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), default=None, comment="备注")
