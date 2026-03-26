from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.class_student_do import SysClassStudent


class UserClassDao:
    """用户班级数据访问层"""

    @classmethod
    async def get_distinct_student_classes(cls, db: AsyncSession) -> list[str]:
        """查询学生班级去重列表"""
        classes_expr = func.trim(SysClassStudent.classes)
        query = (
            select(classes_expr)
            .where(
                SysClassStudent.del_flag == "0",
                SysClassStudent.classes.isnot(None),
                classes_expr != "",
            )
            .distinct()
            .order_by(classes_expr)
        )
        result = await db.execute(query)
        return [row[0] for row in result.fetchall() if row[0]]
