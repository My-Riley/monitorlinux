from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.emotion_anxiety_mapping_dao import EmotionAnxietyMappingDao
from module_camera.entity.do.emotion_anxiety_mapping_do import EmotionAnxietyMapping


class EmotionAnxietyMappingService:
    """情绪焦虑映射服务层"""

    @classmethod
    async def get_mapping_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        return await EmotionAnxietyMappingDao.get_mapping_list(db, query_params, is_page)

    @classmethod
    async def get_mapping_dict(cls, db: AsyncSession) -> Dict[str, int]:
        return await EmotionAnxietyMappingDao.get_mapping_dict(db)

    @classmethod
    async def get_mapping_detail(cls, db: AsyncSession, mapping_id: int):
        return await EmotionAnxietyMappingDao.get_mapping_by_id(db, mapping_id)

    @classmethod
    async def add_mapping(cls, db: AsyncSession, data: Dict[str, Any]):
        mapping = EmotionAnxietyMapping(
            emotion_en=data.get("emotionEn"),
            emotion_cn=data.get("emotionCn"),
            anxiety_level=int(data.get("anxietyLevel")),
            anxiety_name=data.get("anxietyName"),
            create_time=datetime.now(),
        )
        return await EmotionAnxietyMappingDao.add_mapping(db, mapping)

    @classmethod
    async def update_mapping(cls, db: AsyncSession, mapping_id: int, data: Dict[str, Any]):
        update_data = {
            "emotion_en": data.get("emotionEn"),
            "emotion_cn": data.get("emotionCn"),
            "anxiety_level": int(data.get("anxietyLevel")) if data.get("anxietyLevel") is not None else None,
            "anxiety_name": data.get("anxietyName"),
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}
        await EmotionAnxietyMappingDao.update_mapping(db, mapping_id, update_data)

    @classmethod
    async def delete_mapping(cls, db: AsyncSession, mapping_id: int):
        await EmotionAnxietyMappingDao.delete_mapping(db, mapping_id)
