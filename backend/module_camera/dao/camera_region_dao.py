from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.camera_region_do import Region


class RegionDao:
    """区域数据访问层"""

    @classmethod
    async def get_region_list(cls, db: AsyncSession, query_params: dict):
        """获取区域列表"""
        query = select(Region).where(Region.del_flag == "0")
        if query_params.get("region_name"):
            query = query.where(Region.region_name.like(f"%{query_params['region_name']}%"))
        if query_params.get("status"):
            query = query.where(Region.status == query_params["status"])

        query = query.order_by(Region.order_num)
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_region_by_id(cls, db: AsyncSession, region_id: int):
        """根据ID获取区域"""
        query = select(Region).where(Region.region_id == region_id, Region.del_flag == "0")
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def add_region(cls, db: AsyncSession, region: Region):
        """新增区域"""
        db.add(region)
        await db.commit()
        await db.refresh(region)
        return region

    @classmethod
    async def update_region(cls, db: AsyncSession, region_id: int, update_data: dict):
        """更新区域"""
        query = update(Region).where(Region.region_id == region_id).values(**update_data)
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete_region(cls, db: AsyncSession, region_id: int):
        """删除区域"""
        # 逻辑删除
        query = update(Region).where(Region.region_id == region_id).values(del_flag="2")
        await db.execute(query)
        await db.commit()

    @classmethod
    async def check_region_has_children(cls, db: AsyncSession, region_id: int):
        """检查是否有子区域"""
        query = select(Region).where(Region.parent_id == region_id, Region.del_flag == "0")
        result = await db.execute(query)
        return result.first() is not None
