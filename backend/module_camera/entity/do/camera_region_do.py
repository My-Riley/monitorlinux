from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from config.database import Base


class Region(Base):
    """摄像头区域表 - 对应 sys_camera_region"""

    __tablename__ = "sys_camera_region"
    __table_args__ = {"comment": "摄像头区域表"}

    region_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment="区域id")
    parent_id = Column(BigInteger, default=0, comment="父区域id")
    ancestors = Column(String(50), default="", comment="祖级列表")
    region_name = Column(String(30), default="", comment="区域名称")
    order_num = Column(Integer, default=0, comment="显示顺序")
    address = Column(String(255), default=None, comment="区域地址")
    status = Column(String(1), default="0", comment="区域状态（0正常 1停用）")
    del_flag = Column(String(1), default="0", comment="删除标志（0代表存在 2代表删除）")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, default=None, onupdate=datetime.now, comment="更新时间")
