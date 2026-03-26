from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.camera_dao import CameraDao
from module_camera.entity.do.camera_do import Camera


class CameraService:
    """摄像头管理服务层"""

    @classmethod
    async def get_camera_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        return await CameraDao.get_camera_list(db, query_params, is_page)

    @classmethod
    async def get_camera_by_region(cls, db: AsyncSession, region_id: int):
        return await CameraDao.get_camera_by_region_id(db, region_id)

    @classmethod
    async def get_camera_detail(cls, db: AsyncSession, camera_id: int):
        return await CameraDao.get_camera_by_id(db, camera_id)

    @classmethod
    async def add_camera(cls, db: AsyncSession, data: Dict[str, Any], current_user_name: str):
        # 检查IP是否已存在
        camera_ip = data.get("cameraIp") or data.get("ipAddr")
        if camera_ip:
            existing = await CameraDao.get_camera_by_ip(db, camera_ip)
            if existing:
                raise ValueError(f"摄像头IP {camera_ip} 已存在，请勿重复添加")

        camera = Camera(
            camera_name=data.get("cameraName") or data.get("liftName"),
            region_id=int(data.get("regionId")) if data.get("regionId") else None,
            status=data.get("status", "0"),
            username=data.get("username") or data.get("cameraName"),
            password=data.get("password") or data.get("cameraPassword"),
            ip_addr=camera_ip,
            port=data.get("port") or data.get("cameraPort"),
            rtsp_port=data.get("rtspPort") or data.get("cameraRtspPort"),
            protocol=data.get("protocol"),
            brand=data.get("brand"),
            line=data.get("line", "0"),
            create_by=current_user_name,
            create_time=datetime.now(),
            remark=data.get("remark"),
        )
        return await CameraDao.add_camera(db, camera)

    @classmethod
    async def update_camera(cls, db: AsyncSession, camera_id: int, data: Dict[str, Any], current_user_name: str):
        update_data = {
            "camera_name": data.get("cameraName") or data.get("liftName"),
            "region_id": int(data.get("regionId")) if data.get("regionId") else None,
            "status": data.get("status"),
            "username": data.get("username") or data.get("cameraName"),
            "password": data.get("password") or data.get("cameraPassword"),
            "ip_addr": data.get("cameraIp") or data.get("ipAddr"),
            "port": data.get("port") or data.get("cameraPort"),
            "rtsp_port": data.get("rtspPort") or data.get("cameraRtspPort"),
            "protocol": data.get("protocol"),
            "brand": data.get("brand"),
            "line": data.get("line"),
            "update_by": current_user_name,
            "update_time": datetime.now(),
            "remark": data.get("remark"),
        }
        # 过滤 None
        update_data = {k: v for k, v in update_data.items() if v is not None}
        await CameraDao.update_camera(db, camera_id, update_data)

    @classmethod
    async def delete_camera(cls, db: AsyncSession, camera_ids: str):
        ids = camera_ids.split(",")
        for cid in ids:
            if cid:
                await CameraDao.delete_camera(db, int(cid))
