from datetime import datetime, timedelta
from typing import Any, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.semester_cycle_dao import SemesterCycleDao
from module_camera.dao.semester_dao import SemesterDao
from module_camera.entity.do.semester_cycle_do import SysSemesterCycle
from module_camera.entity.do.semester_do import SysSemester


class SemesterService:
    @staticmethod
    def _semester_to_dict(semester: SysSemester) -> dict[str, Any]:
        return {
            "id": semester.id,
            "name": semester.name,
            "start": semester.start_date.strftime("%Y-%m-%d") if semester.start_date else None,
            "end": semester.end_date.strftime("%Y-%m-%d") if semester.end_date else None,
            "weeks": semester.weeks,
            "status": semester.status,
            "orderNum": semester.order_num,
            "remark": semester.remark,
        }

    @staticmethod
    def _cycle_to_dict(cycle: SysSemesterCycle) -> dict[str, Any]:
        return {
            "cycleId": cycle.cycle_id,
            "semesterId": cycle.semester_id,
            "weekNum": cycle.week_num,
            "name": cycle.name,
            "startDate": cycle.start_date.strftime("%Y-%m-%d") if cycle.start_date else None,
            "endDate": cycle.end_date.strftime("%Y-%m-%d") if cycle.end_date else None,
            "status": cycle.status,
            "orderNum": cycle.order_num,
            "remark": cycle.remark,
        }

    @classmethod
    async def _sync_semester_from_cycles(
        cls,
        db: AsyncSession,
        semester: SysSemester,
        min_weeks: Optional[int] = None,
    ) -> None:
        if not semester:
            return
        cycles = await SemesterCycleDao.list_cycles_raw(db, semester.id)
        weeks = int(semester.weeks or 0)
        if min_weeks is not None and min_weeks > weeks:
            weeks = int(min_weeks)
        max_week = 0
        for c in cycles:
            if c.week_num is None:
                continue
            try:
                max_week = max(max_week, int(c.week_num))
            except Exception:
                continue
        if max_week > weeks:
            weeks = max_week
        if weeks > 0 and weeks != int(semester.weeks or 0):
            semester.weeks = weeks
        if semester.start_date and weeks > 0:
            min_end = semester.start_date + timedelta(days=weeks * 7 - 1)
            max_end = None
            for c in cycles:
                if c.end_date and (max_end is None or c.end_date > max_end):
                    max_end = c.end_date
                if c.week_num and int(c.week_num) == weeks and c.end_date:
                    # If this is the last week, ensure semester ends at least then
                    if c.end_date > min_end:
                        min_end = c.end_date

            new_end = min_end
            if max_end and max_end > new_end:
                new_end = max_end
            semester.end_date = new_end

    @classmethod
    async def get_all_semesters(cls, db: AsyncSession) -> list[dict[str, Any]]:
        semesters = await SemesterDao.list_semesters(db)
        return [cls._semester_to_dict(s) for s in semesters]

    @classmethod
    async def get_semester_by_id(cls, db: AsyncSession, semester_id: str) -> Optional[dict[str, Any]]:
        semester = await SemesterDao.get_semester_entity_by_id(db, semester_id)
        return cls._semester_to_dict(semester) if semester else None

    @classmethod
    async def get_current_semester(cls, db: AsyncSession) -> Optional[dict[str, Any]]:
        semester = await SemesterDao.get_current_semester_entity(db)
        return cls._semester_to_dict(semester) if semester else None

    @classmethod
    async def get_semester_weeks(cls, db: AsyncSession, semester_id: str) -> list[dict[str, Any]]:
        semester = await cls.get_semester_by_id(db, semester_id)
        if not semester:
            return []
        cycles = await SemesterCycleDao.list_cycles_raw(db, semester_id)
        cycle_by_week: dict[int, SysSemesterCycle] = {}
        for c in cycles:
            if c.week_num is None:
                continue
            week = int(c.week_num)
            if week not in cycle_by_week:
                cycle_by_week[week] = c
        start_date_str = semester.get("start")
        if not start_date_str:
            return []
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        week_count = int(semester.get("weeks") or 0)
        weeks: list[dict[str, Any]] = []
        for i in range(1, week_count + 1):
            week_start = start_dt + timedelta(weeks=i - 1)
            week_end = week_start + timedelta(days=6)
            cycle = cycle_by_week.get(i)
            if cycle:
                weeks.append(
                    {
                        "cycleId": cycle.cycle_id,
                        "semesterId": cycle.semester_id,
                        "weekNum": i,
                        "name": (cycle.name or "").strip() or f"第{i}周",
                        "startDate": cycle.start_date.strftime("%Y-%m-%d")
                        if cycle.start_date
                        else week_start.strftime("%Y-%m-%d"),
                        "endDate": cycle.end_date.strftime("%Y-%m-%d")
                        if cycle.end_date
                        else week_end.strftime("%Y-%m-%d"),
                        "status": cycle.status,
                        "orderNum": cycle.order_num,
                        "remark": cycle.remark,
                    }
                )
            else:
                weeks.append(
                    {
                        "weekNum": i,
                        "name": f"第{i}周",
                        "startDate": week_start.strftime("%Y-%m-%d"),
                        "endDate": week_end.strftime("%Y-%m-%d"),
                    }
                )
        return weeks

    @classmethod
    async def get_week_date_range(
        cls, db: AsyncSession, semester_id: str, week_num: int
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        semester = await cls.get_semester_by_id(db, semester_id)
        if not semester:
            return None, None
        cycle = await SemesterCycleDao.get_cycle_by_semester_and_week(db, semester_id, week_num)
        if cycle and cycle.start_date and cycle.end_date:
            start_dt = datetime.combine(cycle.start_date, datetime.min.time())
            end_dt = datetime.combine(cycle.end_date, datetime.max.time()).replace(microsecond=0)
            return start_dt, end_dt
        total_weeks = int(semester.get("weeks") or 0)
        if not week_num or week_num < 1 or week_num > total_weeks:
            return None, None
        start_date_str = semester.get("start")
        if not start_date_str:
            return None, None
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        week_start = start_dt + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return week_start, week_end

    @classmethod
    async def get_semester_date_range(
        cls, db: AsyncSession, semester_id: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        semester = await cls.get_semester_by_id(db, semester_id)
        if not semester:
            return None, None
        start_date_str = semester.get("start")
        end_date_str = semester.get("end")
        if not start_date_str or not end_date_str:
            return None, None
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        return start_dt, end_dt

    @classmethod
    async def create_semester(cls, db: AsyncSession, data: dict[str, Any]) -> None:
        await SemesterDao.ensure_seeded(db)
        semester_id = (data.get("id") or "").strip()
        name = (data.get("name") or "").strip()
        start_str = (data.get("start") or data.get("startDate") or "").strip()
        end_str = (data.get("end") or data.get("endDate") or "").strip()
        weeks = int(data.get("weeks") or 20)
        status = (data.get("status") or "0").strip()
        order_num = int(data.get("orderNum") or 0)
        remark = data.get("remark")

        start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None
        if not name or not start_date or not end_date:
            raise ValueError("参数不完整")
        if start_date > end_date:
            raise ValueError("开始日期不能晚于结束日期")
        if weeks < 1:
            raise ValueError("周数必须大于0")
        min_end_date = start_date + timedelta(days=weeks * 7 - 1)
        if end_date < min_end_date:
            raise ValueError("结束日期需覆盖周数范围")

        if not semester_id:
            start_year = int(start_date.year)
            start_month = int(start_date.month)
            term = 1 if start_month >= 8 else 2
            academic_start_year = start_year if term == 1 else start_year - 1
            academic_end_year = academic_start_year + 1
            base_id = f"{academic_start_year}-{academic_end_year}-{term}"
            candidate = base_id
            if await SemesterDao.semester_id_exists(db, candidate):
                for i in range(1, 100):
                    candidate = f"{base_id}-{i}"
                    if not await SemesterDao.semester_id_exists(db, candidate):
                        semester_id = candidate
                        break
            else:
                semester_id = candidate

        if not semester_id:
            raise ValueError("无法生成学期ID")

        if await SemesterDao.semester_id_exists(db, semester_id):
            raise ValueError("学期ID已存在")

        db.add(
            SysSemester(
                id=semester_id,
                name=name,
                start_date=start_date,
                end_date=end_date,
                weeks=weeks,
                status=status,
                order_num=order_num,
                create_by="admin",
                remark=remark,
            )
        )
        await db.flush()
        await db.commit()

    @classmethod
    async def update_semester(cls, db: AsyncSession, data: dict[str, Any]) -> None:
        semester_id = data.get("id")
        if not semester_id:
            raise ValueError("ID不能为空")
        semester = await SemesterDao.get_semester_entity_by_id(db, semester_id)
        if not semester:
            raise ValueError("学期不存在")

        name = (data.get("name") or "").strip()
        start_str = (data.get("start") or data.get("startDate") or "").strip()
        end_str = (data.get("end") or data.get("endDate") or "").strip()
        weeks = int(data.get("weeks") or 0)

        if name:
            semester.name = name
        if start_str:
            semester.start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        if end_str:
            semester.end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        if weeks > 0:
            semester.weeks = weeks
        if "status" in data:
            semester.status = data.get("status")
        if "orderNum" in data:
            semester.order_num = int(data.get("orderNum"))
        if "remark" in data:
            semester.remark = data.get("remark")

        if semester.start_date > semester.end_date:
            raise ValueError("开始日期不能晚于结束日期")

        await db.commit()

    @classmethod
    async def delete_semester(cls, db: AsyncSession, semester_ids: str) -> None:
        if not semester_ids:
            return
        ids = semester_ids.split(",")
        for id in ids:
            await SemesterDao.delete_semester_by_id(db, id)
        await db.commit()

    @classmethod
    async def get_cycles(cls, db: AsyncSession, semester_id: str) -> list[dict[str, Any]]:
        cycles = await SemesterCycleDao.list_cycles_raw(db, semester_id)
        return [cls._cycle_to_dict(c) for c in cycles]

    @classmethod
    async def create_cycle(cls, db: AsyncSession, data: dict[str, Any]) -> None:
        await SemesterDao.ensure_seeded(db)
        semester_id = (data.get("semesterId") or data.get("semester_id") or "").strip()
        week_num = data.get("weekNum") if data.get("weekNum") is not None else data.get("week_num")
        name = (data.get("name") or "").strip()
        start_str = (data.get("startDate") or data.get("start_date") or "").strip()
        end_str = (data.get("endDate") or data.get("end_date") or "").strip()
        status = (data.get("status") or "0").strip()
        order_num = int(data.get("orderNum") or 0)
        remark = data.get("remark")

        try:
            week_num = int(week_num)
        except Exception:
            week_num = None
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else None
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else None

        if not semester_id or not week_num or not start_date or not end_date:
            raise ValueError("参数不完整")
        if start_date > end_date:
            raise ValueError("开始日期不能晚于结束日期")

        if not name:
            name = f"第{week_num}周"

        semester_entity = await SemesterDao.get_semester_entity_by_id(db, semester_id)
        if not semester_entity:
            raise ValueError("学期不存在")
        if week_num < 1:
            raise ValueError("周次必须大于0")
        if semester_entity.start_date and start_date < semester_entity.start_date:
            raise ValueError("周期开始日期不能早于学期开始日期")

        if await SemesterCycleDao.get_cycle_by_semester_and_week(db, semester_id, week_num):
            raise ValueError("该学期周次已存在")

        cycle = SysSemesterCycle(
            semester_id=semester_id,
            week_num=week_num,
            name=name,
            start_date=start_date,
            end_date=end_date,
            status=status,
            order_num=order_num,
            create_by="admin",
            remark=remark,
        )
        db.add(cycle)
        await db.flush()
        await cls._sync_semester_from_cycles(db, semester_entity, min_weeks=week_num)
        await db.commit()

    @classmethod
    async def update_cycle(cls, db: AsyncSession, data: dict[str, Any]) -> None:
        await SemesterDao.ensure_seeded(db)
        cycle_id = data.get("cycleId") if data.get("cycleId") is not None else data.get("cycle_id")
        try:
            cycle_id = int(cycle_id)
        except Exception:
            cycle_id = None
        if not cycle_id:
            raise ValueError("周期ID不能为空")

        cycle = await SemesterCycleDao.get_cycle_by_id(db, cycle_id)
        if not cycle:
            raise ValueError("周期不存在")

        original_semester_id = cycle.semester_id
        original_week_num = cycle.week_num

        if data.get("semesterId") is not None or data.get("semester_id") is not None:
            cycle.semester_id = (data.get("semesterId") or data.get("semester_id") or cycle.semester_id).strip()
        if data.get("weekNum") is not None or data.get("week_num") is not None:
            try:
                cycle.week_num = int(data.get("weekNum") if data.get("weekNum") is not None else data.get("week_num"))
            except Exception:
                pass
        if data.get("name") is not None:
            cycle.name = (data.get("name") or "").strip()
        if data.get("startDate") is not None or data.get("start_date") is not None:
            start_str = (data.get("startDate") or data.get("start_date") or "").strip()
            if start_str:
                cycle.start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        if data.get("endDate") is not None or data.get("end_date") is not None:
            end_str = (data.get("endDate") or data.get("end_date") or "").strip()
            if end_str:
                cycle.end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        if data.get("status") is not None:
            cycle.status = (data.get("status") or cycle.status).strip()
        if data.get("orderNum") is not None:
            cycle.order_num = int(data.get("orderNum") or cycle.order_num)
        if data.get("remark") is not None:
            cycle.remark = data.get("remark")

        if cycle.start_date and cycle.end_date and cycle.start_date > cycle.end_date:
            raise ValueError("开始日期不能晚于结束日期")
        if cycle.semester_id != original_semester_id or cycle.week_num != original_week_num:
            exists = await SemesterCycleDao.get_cycle_by_semester_and_week(db, cycle.semester_id, cycle.week_num)
            if exists and exists.cycle_id != cycle.cycle_id:
                raise ValueError("该学期周次已存在")

        semester_entity = await SemesterDao.get_semester_entity_by_id(db, cycle.semester_id)
        if not semester_entity:
            raise ValueError("学期不存在")
        if not cycle.week_num or cycle.week_num < 1:
            raise ValueError("周次必须大于0")
        if semester_entity.start_date and cycle.start_date and cycle.start_date < semester_entity.start_date:
            raise ValueError("周期开始日期不能早于学期开始日期")

        cycle.update_by = "admin"
        await db.flush()
        await cls._sync_semester_from_cycles(db, semester_entity, min_weeks=cycle.week_num)
        await db.commit()

    @classmethod
    async def delete_cycle(cls, db: AsyncSession, cycle_id: int) -> None:
        cycle = await SemesterCycleDao.get_cycle_by_id(db, cycle_id)
        semester_id = cycle.semester_id if cycle else None
        await SemesterCycleDao.delete_cycle(db, cycle_id)
        if semester_id:
            semester_entity = await SemesterDao.get_semester_entity_by_id(db, semester_id)
            if semester_entity:
                await cls._sync_semester_from_cycles(db, semester_entity)
        await db.commit()
