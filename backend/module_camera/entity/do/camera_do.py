from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String

from config.database import Base


class Camera(Base):
    """摄像头信息表 - 对应 sys_camera"""

    __tablename__ = "sys_camera"
    __table_args__ = {"comment": "摄像头表"}

    camera_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment="摄像头ID")
    camera_name = Column(String(100), nullable=False, comment="摄像头名称")
    region_id = Column(BigInteger, default=None, comment="区域ID")
    status = Column(String(1), default="0", comment="状态（0正常 1停用）")
    del_flag = Column(String(1), default="0", comment="删除标志（0代表存在 2代表删除）")
    username = Column(String(50), default=None, comment="登录用户名")
    password = Column(String(50), default=None, comment="登录密码")
    ip_addr = Column(String(50), default=None, comment="IP地址")
    port = Column(String(50), default=None, comment="端口")
    rtsp_port = Column(String(50), default=None, comment="RTSP端口")
    protocol = Column(String(50), default=None, comment="协议")
    brand = Column(String(50), default=None, comment="品牌")
    line = Column(String(2), default="0", comment="线路")
    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, default=None, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), default=None, comment="备注")
