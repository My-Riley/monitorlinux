from sqlalchemy import delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.camera_warn_do import Warn
from utils.page_util import PageUtil


class CameraWarnDao:
    """摄像头预警DAO层"""

    @classmethod
    async def get_warn_list(cls, db: AsyncSession, query_params: dict, is_page: bool = False):
        """获取预警列表"""
        query = select(Warn).order_by(desc(Warn.create_time))

        if query_params.get("warn_name"):
            query = query.where(Warn.warn_name.like(f"%{query_params['warn_name']}%"))
        if query_params.get("status"):
            query = query.where(Warn.status == query_params["status"])
        if query_params.get("warn_level"):
            query = query.where(Warn.warn_level == query_params["warn_level"])

        if is_page:
            return await PageUtil.paginate(db, query, query_params["page_num"], query_params["page_size"], is_page=True)

        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_warn_by_id(cls, db: AsyncSession, warn_id: int):
        """根据ID获取预警"""
        query = select(Warn).where(Warn.warn_id == warn_id)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def add_warn(cls, db: AsyncSession, warn: Warn):
        """新增预警"""
        db.add(warn)
        await db.flush()
        return warn

    @classmethod
    async def update_warn(cls, db: AsyncSession, warn: dict, warn_id: int):
        """更新预警"""
        query = update(Warn).where(Warn.warn_id == warn_id).values(**warn)
        await db.execute(query)

    @classmethod
    async def delete_warn(cls, db: AsyncSession, warn_id: int):
        """删除预警"""
        query = delete(Warn).where(Warn.warn_id == warn_id)
        await db.execute(query)
