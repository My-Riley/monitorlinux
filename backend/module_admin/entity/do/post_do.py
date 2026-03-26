from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String

from config.database import Base


class SysPost(Base):
    """岗位信息表"""

    __tablename__ = "sys_post"
    __table_args__ = {"comment": "岗位信息表"}

    post_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="岗位ID")
    post_code = Column(String(64), nullable=False, comment="岗位编码")
    post_name = Column(String(50), nullable=False, comment="岗位名称")
    post_sort = Column(BigInteger, nullable=False, comment="显示顺序")
    status = Column(CHAR(1), nullable=False, comment="状态")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")
