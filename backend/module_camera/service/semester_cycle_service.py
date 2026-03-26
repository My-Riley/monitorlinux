from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.semester_cycle_dao import SemesterCycleDao
from module_camera.entity.do.semester_cycle_do import SysSemesterCycle


class SemesterCycleService:
    """学期周期服务层"""

    @classmethod
    async def get_cycle_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        return await SemesterCycleDao.get_cycle_list(db, query_params, is_page)

    @classmethod
    async def get_cycle_detail(cls, db: AsyncSession, cycle_id: int):
        return await SemesterCycleDao.get_cycle_by_id(db, cycle_id)

    @classmethod
    async def add_cycle(cls, db: AsyncSession, data: Dict[str, Any], current_user_name: str):
        # 检查是否已存在
        semester_id = data.get("semesterId")
        week_num = int(data.get("weekNum"))

        existing = await SemesterCycleDao.get_cycle_by_semester_and_week(db, semester_id, week_num)
        if existing:
            raise ValueError(f"学期 {semester_id} 第 {week_num} 周已存在")

        cycle = SysSemesterCycle(
            semester_id=semester_id,
            week_num=week_num,
            name=data.get("name", f"第{week_num}周"),
            start_date=datetime.strptime(data.get("startDate"), "%Y-%m-%d").date(),
            end_date=datetime.strptime(data.get("endDate"), "%Y-%m-%d").date(),
            status=data.get("status", "0"),
            order_num=data.get("orderNum", 0),
            create_by=current_user_name,
            create_time=datetime.now(),
            remark=data.get("remark"),
        )
        return await SemesterCycleDao.add_cycle(db, cycle)

    @classmethod
    async def update_cycle(cls, db: AsyncSession, cycle_id: int, data: Dict[str, Any], current_user_name: str):
        update_data = {
            "semester_id": data.get("semesterId"),
            "week_num": int(data.get("weekNum")) if data.get("weekNum") else None,
            "name": data.get("name"),
            "start_date": datetime.strptime(data.get("startDate"), "%Y-%m-%d").date()
            if data.get("startDate")
            else None,
            "end_date": datetime.strptime(data.get("endDate"), "%Y-%m-%d").date() if data.get("endDate") else None,
            "status": data.get("status"),
            "order_num": data.get("orderNum"),
            "update_by": current_user_name,
            "update_time": datetime.now(),
            "remark": data.get("remark"),
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        await SemesterCycleDao.update_cycle(db, cycle_id, update_data)

    @classmethod
    async def delete_cycle(cls, db: AsyncSession, cycle_id: int):
        await SemesterCycleDao.delete_cycle(db, cycle_id)
