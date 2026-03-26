from datetime import date, datetime
from typing import Optional

from sqlalchemy import delete, distinct, func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.course_do import SysCourse
from module_camera.service.semester_service import SemesterService


class CourseDao:
    """课程数据访问层"""

    @classmethod
    async def ensure_schema(cls, db: AsyncSession):
        date_col = await db.execute(text("SHOW COLUMNS FROM sys_course LIKE 'course_date'"))
        if not date_col.first():
            await db.execute(
                text("ALTER TABLE sys_course ADD COLUMN course_date date NULL COMMENT '日期' AFTER class_name")
            )
            await db.commit()

        start_col = await db.execute(text("SHOW COLUMNS FROM sys_course LIKE 'start_time'"))
        if not start_col.first():
            await db.execute(
                text("ALTER TABLE sys_course ADD COLUMN start_time time NULL COMMENT '开始时间' AFTER course_date")
            )
            await db.commit()

        end_col = await db.execute(text("SHOW COLUMNS FROM sys_course LIKE 'end_time'"))
        if not end_col.first():
            await db.execute(
                text("ALTER TABLE sys_course ADD COLUMN end_time time NULL COMMENT '结束时间' AFTER start_time")
            )
            await db.commit()

    @classmethod
    def _build_course_query(
        cls,
        course_name: str = None,
        subject_name: str = None,
        class_name: str = None,
        status: str = None,
        course_date: str = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        query = select(SysCourse)
        if course_name:
            query = query.where(SysCourse.course_name.like(f"%{course_name}%"))
        if subject_name:
            query = query.where(SysCourse.subject_name == subject_name)
        if class_name:
            class_name = str(class_name).strip()
            query = query.where(func.trim(SysCourse.class_name) == class_name)
        if status:
            query = query.where(SysCourse.status == status)
        if course_date:
            target_date = datetime.strptime(course_date, "%Y-%m-%d").date()
            query = query.where(SysCourse.course_date == target_date)
        elif start_date and end_date:
            query = query.where(SysCourse.course_date >= start_date)
            query = query.where(SysCourse.course_date <= end_date)
        return query

    @classmethod
    async def get_course_list(
        cls,
        db: AsyncSession,
        course_name: str = None,
        subject_name: str = None,
        class_name: str = None,
        status: str = None,
        course_date: str = None,
        semester_id: str = None,
        week_num: int = None,
    ):
        """获取课程列表"""
        await cls.ensure_schema(db)
        start_date = None
        end_date = None
        if not course_date and semester_id:
            if week_num:
                week_start, week_end = await SemesterService.get_week_date_range(db, semester_id, week_num)
                if week_start and week_end:
                    start_date = week_start.date()
                    end_date = week_end.date()
            else:
                sem_start, sem_end = await SemesterService.get_semester_date_range(db, semester_id)
                if sem_start and sem_end:
                    start_date = sem_start.date()
                    end_date = sem_end.date()

        query = cls._build_course_query(
            course_name, subject_name, class_name, status, course_date, start_date, end_date
        )
        query = query.order_by(SysCourse.order_num)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_course_page(
        cls,
        db: AsyncSession,
        course_name: str = None,
        subject_name: str = None,
        class_name: str = None,
        status: str = None,
        course_date: str = None,
        semester_id: str = None,
        week_num: int = None,
        page_num: int = 1,
        page_size: int = 10,
    ):
        await cls.ensure_schema(db)
        start_date = None
        end_date = None
        if not course_date and semester_id:
            if week_num:
                week_start, week_end = await SemesterService.get_week_date_range(db, semester_id, week_num)
                if week_start and week_end:
                    start_date = week_start.date()
                    end_date = week_end.date()
            else:
                sem_start, sem_end = await SemesterService.get_semester_date_range(db, semester_id)
                if sem_start and sem_end:
                    start_date = sem_start.date()
                    end_date = sem_end.date()

        query = cls._build_course_query(
            course_name, subject_name, class_name, status, course_date, start_date, end_date
        )
        count_query = select(func.count()).select_from(query.order_by(None).subquery())
        total = (await db.execute(count_query)).scalar() or 0
        query = query.order_by(SysCourse.order_num).offset((page_num - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return result.scalars().all(), total

    @classmethod
    async def list_course_week_nums(cls, db: AsyncSession, semester_id: str) -> list[int]:
        await cls.ensure_schema(db)
        if not semester_id:
            return []
        sem_start_dt, sem_end_dt = await SemesterService.get_semester_date_range(db, semester_id)
        if not sem_start_dt or not sem_end_dt:
            return []
        semester = await SemesterService.get_semester_by_id(db, semester_id)
        total_weeks = int((semester or {}).get("weeks") or 0)
        start_date = sem_start_dt.date()
        end_date = sem_end_dt.date()
        result = await db.execute(
            select(distinct(SysCourse.course_date)).where(
                SysCourse.course_date.isnot(None),
                SysCourse.course_date >= start_date,
                SysCourse.course_date <= end_date,
            )
        )
        week_nums: set[int] = set()
        for row in result.all():
            course_date = row[0]
            if not course_date:
                continue
            try:
                week_num = ((course_date - start_date).days // 7) + 1
            except Exception:
                continue
            if week_num < 1:
                continue
            if total_weeks and week_num > total_weeks:
                continue
            week_nums.add(int(week_num))
        return sorted(week_nums)

    @classmethod
    async def get_course_by_id(cls, db: AsyncSession, course_id: int):
        """根据ID获取课程"""
        await cls.ensure_schema(db)
        query = select(SysCourse).where(SysCourse.course_id == course_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def add_course(cls, db: AsyncSession, course: dict):
        """新增课程"""
        await cls.ensure_schema(db)
        db_course = SysCourse(**course)
        db.add(db_course)
        await db.flush()
        return db_course

    @classmethod
    async def update_course(cls, db: AsyncSession, course: dict):
        """更新课程"""
        await cls.ensure_schema(db)
        course_id = course.pop("course_id")
        query = update(SysCourse).where(SysCourse.course_id == course_id).values(**course)
        await db.execute(query)

    @classmethod
    async def delete_course(cls, db: AsyncSession, course_ids: list):
        """删除课程"""
        query = delete(SysCourse).where(SysCourse.course_id.in_(course_ids))
        await db.execute(query)

    @classmethod
    async def get_distinct_subject_names(cls, db: AsyncSession) -> list[str]:
        """查询课程学科去重列表"""
        subject_expr = func.trim(SysCourse.subject_name)
        query = (
            select(subject_expr)
            .where(
                SysCourse.subject_name.isnot(None),
                subject_expr != "",
            )
            .distinct()
            .order_by(subject_expr)
        )
        result = await db.execute(query)
        return [row[0] for row in result.fetchall() if row[0]]
