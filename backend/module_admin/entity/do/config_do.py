from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String

from config.database import Base


class SysConfig(Base):
    """参数配置表"""

    __tablename__ = "sys_config"
    __table_args__ = {"comment": "参数配置表"}

    config_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="参数主键")
    config_name = Column(String(100), nullable=True, comment="参数名称")
    config_key = Column(String(100), nullable=True, comment="参数键名")
    config_value = Column(String(500), nullable=True, comment="参数键值")
    config_type = Column(CHAR(1), nullable=True, server_default="N", comment="系统内置")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")
