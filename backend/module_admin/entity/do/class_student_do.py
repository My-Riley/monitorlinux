# student_do.py
from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, Integer, String

from config.database import Base


class SysClassStudent(Base):
    """班级学生信息表"""

    __tablename__ = "sys_class_student"
    __table_args__ = {"comment": "班级学生信息表"}

    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment="主键")
    student_id = Column(String(50), nullable=False, unique=True, comment="学号（唯一标识）")
    student_name = Column(String(30), nullable=False, comment="学生姓名")
    classes = Column(String(30), nullable=False, comment="班级")
    email = Column(String(50), nullable=True, comment="邮箱")
    grade = Column(String(50), nullable=True, comment="年级")
    phonenumber = Column(String(11), nullable=True, comment="手机号码")
    sex = Column(String(11), nullable=True, server_default="2", comment="性别（0男 1女 2未知）")
    age = Column(Integer, nullable=True, comment="年龄")
    face_image = Column(String(64), nullable=True, comment="人脸图像")
    status = Column(CHAR(1), nullable=True, server_default="0", comment="状态（0正常 1停用）")
    del_flag = Column(CHAR(1), nullable=True, server_default="0", comment="是否删除（0存在 2删除）")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), nullable=True, comment="备注")
