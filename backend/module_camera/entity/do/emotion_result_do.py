from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, String, Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from config.database import Base


class EmotionAnalysisResult(Base):
    """情绪识别结果表 - 对应 sys_emotion_result"""

    __tablename__ = "sys_emotion_result"
    __table_args__ = {"comment": "情绪识别结果表"}

    result_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment="结果ID")
    student_id = Column(String(50), default=None, comment="学号")
    student_name = Column(String(50), default=None, comment="学生姓名")
    emotion = Column(String(50), nullable=False, comment="情绪")
    camera_ip = Column(String(50), default=None, comment="摄像头IP")
    image_base64 = Column(MEDIUMTEXT, nullable=True, comment="图片Base64")
    image_path = Column(String(255), default=None, comment="图片路径")
    url = Column(String(255), default=None, comment="URL")
    statistics = Column(Text, nullable=True, comment="统计信息")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
