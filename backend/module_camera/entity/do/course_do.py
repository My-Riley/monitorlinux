from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, String, Time

from config.database import Base


class SysCourse(Base):
    """课程时间表"""

    __tablename__ = "sys_course"
    __table_args__ = {"comment": "课程表"}

    course_id = Column(Integer, primary_key=True, autoincrement=True, comment="课程ID")
    course_name = Column(String(50), nullable=False, comment="课节")
    subject_name = Column(String(50), default=None, comment="学科名称")
    class_name = Column(String(50), default=None, comment="班级")
    course_date = Column(Date, default=None, comment="日期")
    start_time = Column(Time, default=None, comment="开始时间")
    end_time = Column(Time, default=None, comment="结束时间")
    order_num = Column(Integer, default=0, comment="排序")
    status = Column(String(1), default="0", comment="状态(0正常 1停用)")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), default=None, comment="备注")
