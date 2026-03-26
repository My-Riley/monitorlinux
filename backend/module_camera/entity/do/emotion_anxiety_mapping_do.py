from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from config.database import Base


class EmotionAnxietyMapping(Base):
    """情绪焦虑映射表 - 对应 sys_emotion_anxiety_mapping"""

    __tablename__ = "sys_emotion_anxiety_mapping"
    __table_args__ = {"comment": "情绪焦虑映射表"}

    mapping_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="主键ID")
    emotion_en = Column(String(50), nullable=False, comment="情绪英文名称")
    emotion_cn = Column(String(50), nullable=False, comment="情绪中文名称")
    anxiety_level = Column(Integer, nullable=False, comment="焦虑程度(0:无焦虑, 1:低度焦虑, 2:中度焦虑, 3:高度焦虑)")
    anxiety_name = Column(String(50), nullable=False, comment="焦虑程度名称")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
