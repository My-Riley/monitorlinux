from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.camera_do import Camera
from utils.page_util import PageUtil


class CameraDao:
    """摄像头数据访问层 - 对应 sys_camera 表"""

    @classmethod
    async def get_camera_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        """获取摄像头列表"""
        query = select(Camera).where(Camera.del_flag == "0")
        if query_params.get("camera_name"):
            query = query.where(Camera.camera_name.like(f"%{query_params['camera_name']}%"))
        if query_params.get("status"):
            query = query.where(Camera.status == query_params["status"])
        if query_params.get("region_id"):
            query = query.where(Camera.region_id == query_params["region_id"])
        query = query.order_by(Camera.create_time.desc())

        page_num = query_params.get("page_num", 1)
        page_size = query_params.get("page_size", 10)
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def get_camera_by_id(cls, db: AsyncSession, camera_id: int):
        """根据ID获取摄像头"""
        query = select(Camera).where(Camera.camera_id == camera_id, Camera.del_flag == "0")
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def get_camera_by_region_id(cls, db: AsyncSession, region_id: int):
        """根据区域ID获取摄像头列表"""
        query = select(Camera).where(Camera.region_id == region_id, Camera.del_flag == "0")
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_camera_by_ip(cls, db: AsyncSession, ip_addr: str, exclude_id: int = None):
        """根据IP获取摄像头，用于检查IP唯一性"""
        query = select(Camera).where(Camera.ip_addr == ip_addr, Camera.del_flag == "0")
        if exclude_id:
            query = query.where(Camera.camera_id != exclude_id)
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def add_camera(cls, db: AsyncSession, camera: Camera):
        """新增摄像头"""
        db.add(camera)
        await db.commit()
        await db.refresh(camera)
        return camera

    @classmethod
    async def update_camera(cls, db: AsyncSession, camera_id: int, update_data: dict):
        """更新摄像头"""
        query = update(Camera).where(Camera.camera_id == camera_id).values(**update_data)
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete_camera(cls, db: AsyncSession, camera_id: int):
        """删除摄像头（逻辑删除）"""
        query = update(Camera).where(Camera.camera_id == camera_id).values(del_flag="2")
        await db.execute(query)
        await db.commit()
