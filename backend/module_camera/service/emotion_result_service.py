from datetime import datetime
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.emotion_result_dao import EmotionResultDao
from utils.page_util import PageResponseModel


class EmotionResultService:
    @classmethod
    async def get_emotion_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True) -> PageResponseModel:
        return await EmotionResultDao.get_emotion_list(db, query_params, is_page)

    @classmethod
    async def get_focus_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True) -> PageResponseModel:
        if hasattr(EmotionResultDao, "get_focus_list"):
            return await EmotionResultDao.get_focus_list(db, query_params, is_page)
        return []

    @classmethod
    async def get_unknown_list(cls, db: AsyncSession, query_params: dict, is_page: bool = True):
        return await EmotionResultDao.get_unknown_list(db, query_params, is_page)

    @classmethod
    async def get_emotion_by_id(cls, db: AsyncSession, emotion_id: int):
        return await EmotionResultDao.get_emotion_by_id(db, emotion_id)

    @classmethod
    async def add_emotion(cls, db: AsyncSession, data: Dict[str, Any]):
        from module_camera.entity.do.emotion_result_do import EmotionAnalysisResult

        emotion = EmotionAnalysisResult(
            student_name=data.get("studentName") or data.get("name"),
            student_id=data.get("studentId") or data.get("student") or data.get("Student"),
            emotion=data.get("emotion"),
            camera_ip=data.get("cameraIp") or data.get("camera_ip"),
            image_base64=data.get("imageBase64"),
            create_time=datetime.now(),
            url=data.get("url"),
            statistics=data.get("statistics", data.get("emotion", "")),
        )
        return await EmotionResultDao.add_emotion(db, emotion)

    @classmethod
    async def update_emotion(cls, db: AsyncSession, emotion_id: int, update_data: dict):
        if hasattr(EmotionResultDao, "update_emotion"):
            return await EmotionResultDao.update_emotion(db, emotion_id, update_data)
        return None

    @classmethod
    async def delete_emotion(cls, db: AsyncSession, emotion_id: int):
        return await EmotionResultDao.delete_emotion(db, emotion_id)

    # --- 图表类方法（全部委托给 DAO）---
    @classmethod
    async def get_user_list(cls, db: AsyncSession):
        return await EmotionResultDao.get_user_list(db)

    @classmethod
    async def get_user_emotion_chart(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_user_emotion_chart(db, query_params)

    @classmethod
    async def get_address_emotion_chart(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_address_emotion_chart(db, query_params)

    @classmethod
    async def get_student_emotion_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_student_emotion_stats(db, query_params)

    @classmethod
    async def get_subject_emotion_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_subject_emotion_stats(db, query_params)

    @classmethod
    async def get_class_emotion_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_class_emotion_stats(db, query_params)

    @classmethod
    async def get_weekly_emotion_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_weekly_emotion_stats(db, query_params)

    @classmethod
    async def get_all_weeks_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_all_weeks_stats(db, query_params)

    @classmethod
    async def get_semester_weeks_stats(cls, db: AsyncSession, query_params: dict):
        if hasattr(EmotionResultDao, "get_semester_weeks_stats"):
            return await EmotionResultDao.get_semester_weeks_stats(db, query_params)
        return {}

    @classmethod
    async def get_semester_week_detail_stats(cls, db: AsyncSession, query_params: dict):
        if hasattr(EmotionResultDao, "get_semester_week_detail_stats"):
            return await EmotionResultDao.get_semester_week_detail_stats(db, query_params)
        return {}

    @classmethod
    async def get_dashboard_overall_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_dashboard_overall_stats(db, query_params)

    @classmethod
    async def get_dashboard_trend_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_dashboard_trend_stats(db, query_params)

    @classmethod
    async def get_dashboard_mood_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_dashboard_mood_stats(db, query_params)

    @classmethod
    async def get_class_anxiety_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_class_anxiety_stats(db, query_params)

    @classmethod
    async def get_class_subject_anxiety_stats(cls, db: AsyncSession, query_params: dict):
        return await EmotionResultDao.get_class_subject_anxiety_stats(db, query_params)
