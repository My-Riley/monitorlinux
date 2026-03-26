from typing import Dict

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.entity.do.emotion_anxiety_mapping_do import EmotionAnxietyMapping
from utils.page_util import PageUtil


class EmotionAnxietyMappingDao:
    """情绪焦虑映射数据访问层"""

    @classmethod
    async def get_mapping_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        query = select(EmotionAnxietyMapping)
        if query_params.get("emotion_en"):
            query = query.where(EmotionAnxietyMapping.emotion_en.like(f"%{query_params['emotion_en']}%"))

        query = query.order_by(EmotionAnxietyMapping.mapping_id.asc())

        page_num = query_params.get("page_num", 1)
        page_size = query_params.get("page_size", 10)
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def get_mapping_dict(cls, db: AsyncSession) -> Dict[str, int]:
        """获取情绪英文名（含大小写）到焦虑等级的映射"""
        result = await db.execute(select(EmotionAnxietyMapping))
        mappings = result.scalars().all()
        mapping_dict = {}
        for m in mappings:
            mapping_dict[m.emotion_en] = m.anxiety_level
            mapping_dict[m.emotion_en.lower()] = m.anxiety_level
        return mapping_dict

    @classmethod
    async def get_mapping_by_id(cls, db: AsyncSession, mapping_id: int):
        query = select(EmotionAnxietyMapping).where(EmotionAnxietyMapping.mapping_id == mapping_id)
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def add_mapping(cls, db: AsyncSession, mapping: EmotionAnxietyMapping):
        db.add(mapping)
        await db.commit()
        await db.refresh(mapping)
        return mapping

    @classmethod
    async def update_mapping(cls, db: AsyncSession, mapping_id: int, update_data: dict):
        query = (
            update(EmotionAnxietyMapping).where(EmotionAnxietyMapping.mapping_id == mapping_id).values(**update_data)
        )
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete_mapping(cls, db: AsyncSession, mapping_id: int):
        query = delete(EmotionAnxietyMapping).where(EmotionAnxietyMapping.mapping_id == mapping_id)
        await db.execute(query)
        await db.commit()
