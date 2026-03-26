from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.semester_do import SysSemester


class SemesterDao:
    @classmethod
    async def ensure_seeded(cls, db: AsyncSession) -> None:
        exists = (await db.execute(select(SysSemester.id).limit(1))).first()
        if exists:
            return
        seeds: list[dict] = []
        if not seeds:
            return
        for sem in seeds:
            start_date = datetime.strptime(sem["start"], "%Y-%m-%d").date()
            end_date = datetime.strptime(sem["end"], "%Y-%m-%d").date()
            db.add(
                SysSemester(
                    id=sem["id"],
                    name=sem["name"],
                    start_date=start_date,
                    end_date=end_date,
                    weeks=int(sem.get("weeks") or 20),
                    status="0",
                    order_num=0,
                    create_by="system",
                    remark=None,
                )
            )
        await db.commit()

    @classmethod
    async def list_semesters(cls, db: AsyncSession) -> list[SysSemester]:
        await cls.ensure_seeded(db)
        result = await db.execute(
            select(SysSemester).order_by(SysSemester.order_num.asc(), SysSemester.start_date.asc())
        )
        return list(result.scalars().all())

    @classmethod
    async def get_semester_entity_by_id(cls, db: AsyncSession, semester_id: str) -> SysSemester | None:
        if not semester_id:
            return None
        await cls.ensure_seeded(db)
        result = await db.execute(select(SysSemester).where(SysSemester.id == semester_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_current_semester_entity(cls, db: AsyncSession) -> SysSemester | None:
        await cls.ensure_seeded(db)
        today = datetime.now().date()
        result = await db.execute(
            select(SysSemester)
            .where(SysSemester.start_date <= today, SysSemester.end_date >= today)
            .order_by(SysSemester.start_date.asc())
            .limit(1)
        )
        semester = result.scalars().first()
        if semester:
            return semester
        latest = await db.execute(select(SysSemester).order_by(SysSemester.start_date.desc()).limit(1))
        return latest.scalars().first()

    @classmethod
    async def semester_id_exists(cls, db: AsyncSession, semester_id: str) -> bool:
        if not semester_id:
            return False
        await cls.ensure_seeded(db)
        exists = await db.execute(select(SysSemester.id).where(SysSemester.id == semester_id).limit(1))
        return bool(exists.first())

    @classmethod
    async def delete_semester_by_id(cls, db: AsyncSession, semester_id: str) -> None:
        await cls.ensure_seeded(db)
        if not semester_id:
            return
        await db.execute(delete(SysSemester).where(SysSemester.id == semester_id))
