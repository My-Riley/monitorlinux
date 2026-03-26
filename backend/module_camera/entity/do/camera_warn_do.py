from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from config.database import Base


class Warn(Base):
    """摄像头预警表 - 对应 sys_camera_warn"""

    __tablename__ = "sys_camera_warn"
    __table_args__ = {"comment": "摄像头预警表"}

    warn_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment="预警id")
    warn_name = Column(String(50), nullable=False, comment="预警名称")
    warn_level = Column(String(1), default="1", comment="预警级别(1:低, 2:中, 3:高)")
    warn_content = Column(String(255), default="", comment="预警内容")
    warn_time = Column(DateTime, default=datetime.now, comment="预警时间")
    camera_id = Column(BigInteger, default=None, comment="摄像头ID")
    camera_name = Column(String(50), default="", comment="摄像头名称")
    status = Column(String(1), default="0", comment="状态(0:未处理, 1:已处理)")
    handle_result = Column(String(255), default="", comment="处理结果")
    handle_time = Column(DateTime, nullable=True, comment="处理时间")
    handle_by = Column(String(64), default="", comment="处理人")
    remark = Column(String(500), default="", comment="备注")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=datetime.now, comment="更新时间")
