from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.dao.user_class_dao import UserClassDao


class UserClassService:
    """用户班级服务层"""

    @classmethod
    async def get_distinct_student_classes(cls, db: AsyncSession) -> list[str]:
        """获取学生班级下拉选项"""
        return await UserClassDao.get_distinct_student_classes(db)

    @classmethod
    async def get_distinct_student_class_options(cls, db: AsyncSession) -> list[dict]:
        classes = await UserClassDao.get_distinct_student_classes(db)
        return [{"classId": c, "className": c} for c in classes if c]
