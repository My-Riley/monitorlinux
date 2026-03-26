from datetime import datetime
from typing import Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import AppConfig
from module_admin.entity.do.log_do import SysOperLog
from module_admin.service.login_service import LoginService
from utils.log_util import logger


class OperLogService:
    """操作日志服务层"""

    # 业务类型映射（参考若依）
    BUSINESS_TYPE_OTHER = 0  # 其它
    BUSINESS_TYPE_INSERT = 1  # 新增
    BUSINESS_TYPE_UPDATE = 2  # 修改
    BUSINESS_TYPE_DELETE = 3  # 删除
    BUSINESS_TYPE_GRANT = 4  # 授权
    BUSINESS_TYPE_EXPORT = 5  # 导出
    BUSINESS_TYPE_IMPORT = 6  # 导入
    BUSINESS_TYPE_FORCE = 7  # 强退
    BUSINESS_TYPE_GENCODE = 8  # 生成代码
    BUSINESS_TYPE_CLEAN = 9  # 清空数据

    # 操作状态
    STATUS_SUCCESS = 0  # 成功
    STATUS_FAIL = 1  # 失败

    # 操作人类别
    OPERATOR_TYPE_MANAGE = 0  # 后台用户
    OPERATOR_TYPE_OTHER = 1  # 其它

    @classmethod
    def _get_business_type_by_method(cls, method: str) -> int:
        """根据HTTP方法推断业务类型"""
        method_upper = method.upper()
        if method_upper == "POST":
            return cls.BUSINESS_TYPE_INSERT
        elif method_upper == "PUT":
            return cls.BUSINESS_TYPE_UPDATE
        elif method_upper == "DELETE":
            return cls.BUSINESS_TYPE_DELETE
        elif method_upper == "GET":
            # GET 请求可能是查询或导出
            return cls.BUSINESS_TYPE_OTHER
        else:
            return cls.BUSINESS_TYPE_OTHER

    @classmethod
    def _get_title_by_path(cls, path: str) -> str:
        """根据路径推断模块标题"""
        # 移除前缀 /dev-api 或 /prod-api
        clean_path = path.replace("/dev-api", "").replace("/prod-api", "")
        # 提取第一个路径段作为模块名
        parts = [p for p in clean_path.split("/") if p]
        if not parts:
            return "未知模块"
        # 映射常见路径到模块名
        module_map = {
            "system": "系统管理",
            "monitor": "系统监控",
            "user": "用户管理",
            "dept": "部门管理",
            "role": "角色管理",
            "menu": "菜单管理",
            "post": "岗位管理",
            "dict": "字典管理",
            "config": "参数设置",
            "camera": "摄像头管理",
            "emotion": "情绪识别",
            "course": "课程管理",
        }
        first_part = parts[0].lower()
        return module_map.get(first_part, parts[0].capitalize())

    @classmethod
    async def record_oper_log(
        cls,
        *,
        request: Request,
        query_db: AsyncSession,
        oper_name: str,
        oper_url: str,
        request_method: str,
        oper_param: Optional[str] = None,
        json_result: Optional[str] = None,
        status: int = STATUS_SUCCESS,
        error_msg: Optional[str] = None,
        cost_time: int = 0,
        dept_name: Optional[str] = None,
        oper_location: Optional[str] = None,
        method: Optional[str] = None,
    ) -> None:
        """记录操作日志（不应影响主流程）

        Args:
            request: FastAPI Request 对象
            query_db: 数据库会话
            oper_name: 操作人员名称
            oper_url: 请求URL
            request_method: HTTP方法
            oper_param: 请求参数（JSON字符串）
            json_result: 返回结果（JSON字符串）
            status: 操作状态（0成功，1失败）
            error_msg: 错误消息
            cost_time: 消耗时间（毫秒）
            dept_name: 部门名称
            oper_location: 操作地点（如果为空，会根据IP自动解析）
        """
        try:
            # 获取客户端IP
            ipaddr = LoginService._get_client_ip(request)

            # 解析操作地点（如果未提供）
            if not oper_location and getattr(AppConfig, "app_ip_location_query", False):
                oper_location = LoginService._resolve_login_location_sync(ipaddr)

            # 推断业务类型
            if hasattr(request.state, "oper_log_business_type"):
                business_type = request.state.oper_log_business_type
            else:
                business_type = cls._get_business_type_by_method(request_method)

            # 推断模块标题
            if hasattr(request.state, "oper_log_title"):
                title = request.state.oper_log_title
            else:
                title = cls._get_title_by_path(oper_url)

            # 限制参数长度（避免过大）
            if oper_param and len(oper_param) > 2000:
                oper_param = oper_param[:2000] + "..."
            if json_result and len(json_result) > 2000:
                json_result = json_result[:2000] + "..."
            if error_msg and len(error_msg) > 2000:
                error_msg = error_msg[:2000] + "..."

            row = SysOperLog(
                title=title,
                business_type=business_type,
                method=method or "",  # 方法名称
                request_method=request_method,
                operator_type=cls.OPERATOR_TYPE_MANAGE,
                oper_name=oper_name or "",
                dept_name=dept_name or "",
                oper_url=oper_url,
                oper_ip=ipaddr,
                oper_location=oper_location or "",
                oper_param=oper_param or "",
                json_result=json_result or "",
                status=status,
                error_msg=error_msg or "",
                oper_time=datetime.now(),
                cost_time=cost_time,
            )
            query_db.add(row)
            await query_db.commit()
        except Exception as e:
            # 记录失败不阻断主流程
            try:
                await query_db.rollback()
            except Exception:
                pass
            logger.error(f"记录操作日志失败: {e}")
