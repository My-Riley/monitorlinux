from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.semester_cycle_do import SysSemesterCycle
from utils.page_util import PageUtil


class SemesterCycleDao:
    """学期周期数据访问层"""

    @classmethod
    async def get_cycle_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        query = select(SysSemesterCycle)
        if query_params.get("semester_id"):
            query = query.where(SysSemesterCycle.semester_id == query_params["semester_id"])

        query = query.order_by(SysSemesterCycle.week_num.asc())

        page_num = query_params.get("page_num", 1)
        page_size = query_params.get("page_size", 10)
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def list_cycles_raw(cls, db: AsyncSession, semester_id: str) -> list[SysSemesterCycle]:
        """获取学期周期列表（返回ORM对象）"""
        if not semester_id:
            return []
        query = (
            select(SysSemesterCycle)
            .where(SysSemesterCycle.semester_id == semester_id)
            .order_by(SysSemesterCycle.week_num.asc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_cycle_by_id(cls, db: AsyncSession, cycle_id: int):
        query = select(SysSemesterCycle).where(SysSemesterCycle.cycle_id == cycle_id)
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def get_cycle_by_semester_and_week(cls, db: AsyncSession, semester_id: str, week_num: int):
        query = select(SysSemesterCycle).where(
            SysSemesterCycle.semester_id == semester_id, SysSemesterCycle.week_num == week_num
        )
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def add_cycle(cls, db: AsyncSession, cycle: SysSemesterCycle):
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        return cycle

    @classmethod
    async def update_cycle(cls, db: AsyncSession, cycle_id: int, update_data: dict):
        query = update(SysSemesterCycle).where(SysSemesterCycle.cycle_id == cycle_id).values(**update_data)
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete_cycle(cls, db: AsyncSession, cycle_id: int):
        query = delete(SysSemesterCycle).where(SysSemesterCycle.cycle_id == cycle_id)
        await db.execute(query)
        await db.commit()
