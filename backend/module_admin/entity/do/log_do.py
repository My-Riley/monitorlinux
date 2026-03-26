from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, Text

from config.database import Base


class SysOperLog(Base):
    """操作日志记录"""

    __tablename__ = "sys_oper_log"
    __table_args__ = {"comment": "操作日志记录"}

    oper_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="日志主键")
    title = Column(String(50), nullable=True, comment="模块标题")
    business_type = Column(BigInteger, nullable=True, server_default="0", comment="业务类型")
    method = Column(String(200), nullable=True, comment="方法名称")
    request_method = Column(String(10), nullable=True, comment="请求方式")
    operator_type = Column(BigInteger, nullable=True, server_default="0", comment="操作类别")
    oper_name = Column(String(50), nullable=True, comment="操作人员")
    dept_name = Column(String(50), nullable=True, comment="部门名称")
    oper_url = Column(String(255), nullable=True, comment="请求URL")
    oper_ip = Column(String(128), nullable=True, comment="主机地址")
    oper_location = Column(String(255), nullable=True, comment="操作地点")
    oper_param = Column(Text, nullable=True, comment="请求参数")
    json_result = Column(Text, nullable=True, comment="返回参数")
    status = Column(BigInteger, nullable=True, server_default="0", comment="操作状态")
    error_msg = Column(Text, nullable=True, comment="错误消息")
    oper_time = Column(DateTime, nullable=True, comment="操作时间", default=datetime.now)
    cost_time = Column(BigInteger, nullable=True, server_default="0", comment="消耗时间")


class SysLogininfor(Base):
    """系统访问记录"""

    __tablename__ = "sys_logininfor"
    __table_args__ = {"comment": "系统访问记录"}

    info_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment="访问ID")
    user_name = Column(String(50), nullable=True, comment="用户账号")
    ipaddr = Column(String(128), nullable=True, comment="登录IP地址")
    login_location = Column(String(255), nullable=True, comment="登录地点")
    browser = Column(String(50), nullable=True, comment="浏览器类型")
    os = Column(String(50), nullable=True, comment="操作系统")
    status = Column(String(1), nullable=True, server_default="0", comment="登录状态")
    msg = Column(String(255), nullable=True, comment="提示消息")
    login_time = Column(DateTime, nullable=True, comment="访问时间", default=datetime.now)
