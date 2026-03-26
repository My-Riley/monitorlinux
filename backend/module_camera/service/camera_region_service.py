from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_camera.dao.camera_region_dao import RegionDao
from module_camera.entity.do.camera_region_do import Region
from module_camera.entity.vo.camera_region_vo import RegionModel
from utils.common_util import CamelCaseUtil


class RegionService:
    """区域服务层"""

    @classmethod
    async def get_region_tree_services(cls, query_db: AsyncSession, query_params: dict):
        """获取区域树结构"""
        regions = await RegionDao.get_region_list(query_db, query_params)
        return cls._build_region_tree(regions)

    @classmethod
    def _build_region_tree(cls, regions: list, parent_id: int = 0) -> List[dict]:
        """构建区域树"""
        tree = []
        for region in regions:
            if region.parent_id == parent_id:
                node = CamelCaseUtil.transform_result(region)
                # 适配前端 TreeSelect
                node["id"] = region.region_id
                node["label"] = region.region_name
                children = cls._build_region_tree(regions, region.region_id)
                if children:
                    node["children"] = children
                tree.append(node)
        return tree

    @classmethod
    async def add_region_services(cls, query_db: AsyncSession, region_model: RegionModel, user_name: str):
        """新增区域"""
        region = Region(**region_model.model_dump(exclude_unset=True))
        region.create_by = user_name
        # 处理祖级列表
        if region.parent_id and region.parent_id != 0:
            parent = await RegionDao.get_region_by_id(query_db, region.parent_id)
            if parent:
                region.ancestors = f"{parent.ancestors},{parent.region_id}"
            else:
                region.ancestors = "0"
        else:
            region.ancestors = "0"

        await RegionDao.add_region(query_db, region)

    @classmethod
    async def update_region_services(cls, query_db: AsyncSession, region_model: RegionModel, user_name: str):
        """更新区域"""
        update_data = region_model.model_dump(exclude_unset=True)
        update_data["update_by"] = user_name
        # 不允许修改 region_id
        if "region_id" in update_data:
            del update_data["region_id"]

        # 如果修改了父级，需要更新 ancestors
        if "parent_id" in update_data:
            parent_id = update_data["parent_id"]
            if parent_id and parent_id != 0:
                parent = await RegionDao.get_region_by_id(query_db, parent_id)
                if parent:
                    update_data["ancestors"] = f"{parent.ancestors},{parent.region_id}"
                else:
                    update_data["ancestors"] = "0"
            else:
                update_data["ancestors"] = "0"

        await RegionDao.update_region(query_db, region_model.region_id, update_data)

    @classmethod
    async def delete_region_services(cls, query_db: AsyncSession, region_id: int):
        """删除区域"""
        # 检查是否有子节点
        if await RegionDao.check_region_has_children(query_db, region_id):
            raise ServiceException(message="存在子区域,不允许删除")

        # 检查是否有关联摄像头 (需要在 CameraDao 中实现 check_camera_by_region)
        # 暂时跳过摄像头检查，或后续补充

        await RegionDao.delete_region(query_db, region_id)
