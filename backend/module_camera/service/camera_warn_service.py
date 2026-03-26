from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.camera_warn_dao import CameraWarnDao
from module_camera.entity.do.camera_warn_do import Warn
from module_camera.entity.vo.camera_warn_vo import WarnModel
from utils.common_util import CamelCaseUtil


class CameraWarnService:
    """摄像头预警服务层"""

    @classmethod
    async def get_warn_list_services(cls, query_db: AsyncSession, query_params: dict, is_page: bool = False):
        """获取预警列表"""
        return await CameraWarnDao.get_warn_list(query_db, query_params, is_page)

    @classmethod
    async def get_warn_detail_services(cls, query_db: AsyncSession, warn_id: int):
        """获取预警详情"""
        result = await CameraWarnDao.get_warn_by_id(query_db, warn_id)
        if result:
            return CamelCaseUtil.transform_result(result)
        return None

    @classmethod
    async def add_warn_services(cls, query_db: AsyncSession, warn_data: WarnModel, current_user_name: str):
        """新增预警"""
        warn = Warn(**warn_data.model_dump(exclude_unset=True))
        warn.create_by = current_user_name
        warn.create_time = datetime.now()
        await CameraWarnDao.add_warn(query_db, warn)
        await query_db.commit()
        return warn

    @classmethod
    async def update_warn_services(cls, query_db: AsyncSession, warn_data: WarnModel, current_user_name: str):
        """修改预警"""
        warn_dict = warn_data.model_dump(exclude_unset=True)
        warn_dict["update_by"] = current_user_name
        warn_dict["update_time"] = datetime.now()
        # 如果是处理操作，更新处理时间和处理人
        if warn_dict.get("status") == "1" and not warn_dict.get("handle_time"):
            warn_dict["handle_time"] = datetime.now()
            warn_dict["handle_by"] = current_user_name

        await CameraWarnDao.update_warn(query_db, warn_dict, warn_data.warn_id)
        await query_db.commit()

    @classmethod
    async def delete_warn_services(cls, query_db: AsyncSession, warn_id: int):
        """删除预警"""
        await CameraWarnDao.delete_warn(query_db, warn_id)
        await query_db.commit()
