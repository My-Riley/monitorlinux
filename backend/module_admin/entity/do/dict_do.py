from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Column, DateTime, String

from config.database import Base


class SysDictType(Base):
    """字典类型表"""

    __tablename__ = "sys_dict_type"
    __table_args__ = {"comment": "字典类型表"}

    dict_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="字典主键")
    dict_name = Column(String(100), nullable=True, comment="字典名称")
    dict_type = Column(String(100), nullable=True, unique=True, comment="字典类型")
    status = Column(CHAR(1), nullable=True, server_default="0", comment="状态")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")


class SysDictData(Base):
    """字典数据表"""

    __tablename__ = "sys_dict_data"
    __table_args__ = {"comment": "字典数据表"}

    dict_code = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="字典编码")
    dict_sort = Column(BigInteger, nullable=True, server_default="0", comment="字典排序")
    dict_label = Column(String(100), nullable=True, comment="字典标签")
    dict_value = Column(String(100), nullable=True, comment="字典键值")
    dict_type = Column(String(100), nullable=True, comment="字典类型")
    css_class = Column(String(100), nullable=True, comment="样式属性")
    list_class = Column(String(100), nullable=True, comment="表格回显样式")
    is_default = Column(CHAR(1), nullable=True, server_default="N", comment="是否默认")
    status = Column(CHAR(1), nullable=True, server_default="0", comment="状态")
    create_by = Column(String(64), nullable=True, comment="创建者")
    create_time = Column(DateTime, nullable=True, comment="创建时间", default=datetime.now)
    update_by = Column(String(64), nullable=True, comment="更新者")
    update_time = Column(DateTime, nullable=True, comment="更新时间", default=datetime.now)
    remark = Column(String(500), nullable=True, comment="备注")
