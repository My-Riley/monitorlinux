from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, cast, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.class_student_do import SysClassStudent


class StudentDao:
    """学生数据访问层"""

    @classmethod
    async def get_student_by_id(cls, db: AsyncSession, student_id: str) -> Optional[SysClassStudent]:
        query = select(SysClassStudent).where(SysClassStudent.student_id == student_id, SysClassStudent.del_flag == "0")
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def get_student_by_name(cls, db: AsyncSession, name: str) -> List[SysClassStudent]:
        query = (
            select(SysClassStudent)
            .where(
                SysClassStudent.del_flag == "0",
                or_(
                    SysClassStudent.student_name.like(f"%{name}%"),
                    cast(SysClassStudent.student_id, String).like(f"%{name}%"),
                ),
            )
            .limit(10)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_distinct_grades(cls, db: AsyncSession) -> List[str]:
        query = (
            select(SysClassStudent.grade)
            .where(SysClassStudent.del_flag == "0", SysClassStudent.grade.isnot(None))
            .distinct()
        )
        result = await db.execute(query)
        return [row[0] for row in result.fetchall() if row[0]]

    @classmethod
    async def get_distinct_classes(cls, db: AsyncSession) -> List[str]:
        query = (
            select(SysClassStudent.classes)
            .where(SysClassStudent.del_flag == "0", SysClassStudent.classes.isnot(None))
            .distinct()
        )
        result = await db.execute(query)
        return [row[0] for row in result.fetchall() if row[0]]

    @classmethod
    async def select_page(cls, db: AsyncSession, filters: dict, page_num: int, page_size: int):
        """
        分页查询学生
        """
        query = select(SysClassStudent).where(SysClassStudent.del_flag == "0")

        if filters.get("student_name"):
            query = query.where(SysClassStudent.student_name.like(f"%{filters['student_name']}%"))
        if filters.get("student_id"):
            sid = filters["student_id"]
            query = query.where(SysClassStudent.student_id == sid)
        if filters.get("classes"):
            query = query.where(SysClassStudent.classes == filters["classes"])
        if filters.get("grade"):
            query = query.where(SysClassStudent.grade == filters["grade"])
        if filters.get("status"):
            query = query.where(SysClassStudent.status == filters["status"])
        if filters.get("begin_time"):
            query = query.where(SysClassStudent.create_time >= filters["begin_time"])
        if filters.get("end_time"):
            query = query.where(SysClassStudent.create_time <= filters["end_time"])

        total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0

        items = (
            (
                await db.execute(
                    query.order_by(SysClassStudent.create_time.desc())
                    .offset((page_num - 1) * page_size)
                    .limit(page_size)
                )
            )
            .scalars()
            .all()
        )

        return total, items

    @classmethod
    async def insert_student(cls, db: AsyncSession, student: SysClassStudent):
        db.add(student)
        await db.flush()
        await db.refresh(student)

    @classmethod
    async def update_student(cls, db: AsyncSession, student_id: str, update_data: dict):
        query = (
            update(SysClassStudent)
            .where(SysClassStudent.student_id == student_id, SysClassStudent.del_flag == "0")
            .values(**update_data)
        )
        await db.execute(query)

    @classmethod
    async def delete_student(cls, db: AsyncSession, student_id: str):
        query = update(SysClassStudent).where(SysClassStudent.student_id == student_id).values(del_flag="2")
        await db.execute(query)

    @classmethod
    async def batch_delete_students(cls, db: AsyncSession, student_ids: list[str]):
        query = (
            update(SysClassStudent)
            .where(SysClassStudent.student_id.in_(student_ids))
            .values(del_flag="2", update_time=datetime.now())
        )
        await db.execute(query)

    # 修改：按数据库主键 id 查询
    @classmethod
    async def get_student_by_db_id(cls, db: AsyncSession, db_id: int) -> Optional[SysClassStudent]:
        query = select(SysClassStudent).where(SysClassStudent.id == db_id, SysClassStudent.del_flag == "0")
        result = await db.execute(query)
        return result.scalar()

    # 新增：按学号查（用于唯一性校验）
    @classmethod
    async def get_student_by_student_id(cls, db: AsyncSession, student_id: str) -> Optional[SysClassStudent]:
        query = select(SysClassStudent).where(SysClassStudent.student_id == student_id, SysClassStudent.del_flag == "0")
        result = await db.execute(query)
        return result.scalar()

    # 修改更新方法：按 id 更新
    @classmethod
    async def update_student_by_id(cls, db: AsyncSession, db_id: int, update_data: dict):
        query = (
            update(SysClassStudent)
            .where(SysClassStudent.id == db_id, SysClassStudent.del_flag == "0")
            .values(**update_data)
        )
        await db.execute(query)

    @classmethod
    async def get_students_by_ids(cls, db: AsyncSession, student_ids: List[int]) -> List[SysClassStudent]:
        """根据数据库主键 ID 列表查询学生（用于删除前获取 face_image）"""
        query = select(SysClassStudent).where(SysClassStudent.id.in_(student_ids), SysClassStudent.del_flag == "0")
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_students_by_student_ids(cls, db: AsyncSession, student_ids: List[str]) -> List[SysClassStudent]:
        """根据学号 student_id 列表查询学生（用于删除前获取 face_image）"""
        if not student_ids:
            return []
        query = select(SysClassStudent).where(
            SysClassStudent.student_id.in_(student_ids), SysClassStudent.del_flag == "0"
        )
        result = await db.execute(query)
        return result.scalars().all()
