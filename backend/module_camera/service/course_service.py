import re
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from module_camera.dao.course_dao import CourseDao


class CourseService:
    """课程服务层"""

    @classmethod
    async def get_distinct_subject_names(cls, db: AsyncSession) -> list[str]:
        """获取课程学科下拉选项"""
        return await CourseDao.get_distinct_subject_names(db)

    @staticmethod
    def _infer_period_times(course_name: str):
        mapping = {
            "第一节": ("08:00", "08:45", 1),
            "第二节": ("08:55", "09:40", 2),
            "第三节": ("10:00", "10:45", 3),
            "第四节": ("10:55", "11:40", 4),
            "第五节": ("14:00", "14:45", 5),
            "第六节": ("14:55", "15:40", 6),
            "第七节": ("16:00", "16:45", 7),
            "第八节": ("16:55", "17:40", 8),
            "第九节": ("19:00", "19:45", 9),
            "第1节": ("08:00", "08:45", 1),
            "第2节": ("08:55", "09:40", 2),
            "第3节": ("10:00", "10:45", 3),
            "第4节": ("10:55", "11:40", 4),
            "第5节": ("14:00", "14:45", 5),
            "第6节": ("14:55", "15:40", 6),
            "第7节": ("16:00", "16:45", 7),
            "第8节": ("16:55", "17:40", 8),
            "第9节": ("19:00", "19:45", 9),
        }
        if not course_name or course_name not in mapping:
            return None
        start_s, end_s, order_num = mapping[course_name]
        start_t = datetime.strptime(start_s, "%H:%M").time()
        end_t = datetime.strptime(end_s, "%H:%M").time()
        return start_t, end_t, order_num

    @staticmethod
    def is_valid_course_name(course_name: str) -> bool:
        if course_name is None:
            return False
        s = str(course_name).strip()
        return bool(re.fullmatch(r"第[0-9一二三四五六七八九十百零〇两]+节", s))

    @staticmethod
    def infer_period_time_str(course_name: str):
        inferred = CourseService._infer_period_times(course_name)
        if not inferred:
            return None, None, None
        start_t, end_t, order_num = inferred
        return start_t.strftime("%H:%M"), end_t.strftime("%H:%M"), order_num

    @staticmethod
    def _format_time(t):
        return t.strftime("%H:%M") if t else None

    @staticmethod
    def _parse_time_str(s: str):
        if not s:
            return None
        s = str(s).strip()
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).time()
            except Exception:
                continue
        return None

    @staticmethod
    def is_invalid_time_range(start_time, end_time) -> bool:
        return bool(start_time and end_time and start_time > end_time)

    @classmethod
    async def get_course_list(cls, db: AsyncSession, query_params: dict, is_page: bool = False):
        """获取课程列表"""
        if is_page:
            courses, total = await CourseDao.get_course_page(db, **query_params)
        else:
            courses = await CourseDao.get_course_list(db, **query_params)
            total = len(courses)

        result = []
        for course in courses:
            inferred_start_s, inferred_end_s, _ = cls.infer_period_time_str(course.course_name)
            start_s = cls._format_time(getattr(course, "start_time", None)) or inferred_start_s
            end_s = cls._format_time(getattr(course, "end_time", None)) or inferred_end_s
            result.append(
                {
                    "courseId": course.course_id,
                    "courseName": course.course_name,
                    "subjectName": course.subject_name,
                    "className": course.class_name,
                    "courseDate": course.course_date.strftime("%Y-%m-%d")
                    if getattr(course, "course_date", None)
                    else None,
                    "startTime": start_s,
                    "endTime": end_s,
                    "orderNum": course.order_num,
                    "status": course.status,
                    "createBy": course.create_by,
                    "createTime": course.create_time.strftime("%Y-%m-%d %H:%M:%S") if course.create_time else None,
                }
            )

        if is_page:
            return result, total
        return result

    @classmethod
    async def get_course_by_id(cls, db: AsyncSession, course_id: int):
        """获取课程详情"""
        course = await CourseDao.get_course_by_id(db, course_id)
        if course:
            inferred_start_s, inferred_end_s, _ = cls.infer_period_time_str(course.course_name)
            start_s = cls._format_time(getattr(course, "start_time", None)) or inferred_start_s
            end_s = cls._format_time(getattr(course, "end_time", None)) or inferred_end_s
            return {
                "courseId": course.course_id,
                "courseName": course.course_name,
                "subjectName": course.subject_name,
                "className": course.class_name,
                "courseDate": course.course_date.strftime("%Y-%m-%d") if getattr(course, "course_date", None) else None,
                "startTime": start_s,
                "endTime": end_s,
                "orderNum": course.order_num,
                "status": course.status,
            }
        return None

    @classmethod
    async def add_course(cls, db: AsyncSession, data: dict):
        """新增课程"""
        if not cls.is_valid_course_name(data.get("courseName")):
            raise ValueError("课节格式必须为：第X节（例如：第1节、第11节）")

        inferred_start_s, inferred_end_s, inferred_order = cls.infer_period_time_str(data.get("courseName"))
        course_date = data.get("courseDate")
        start_time = cls._parse_time_str(data.get("startTime")) or cls._parse_time_str(inferred_start_s)
        end_time = cls._parse_time_str(data.get("endTime")) or cls._parse_time_str(inferred_end_s)

        if cls.is_invalid_time_range(start_time, end_time):
            raise ValueError("课节开始时间不能晚于结束时间")

        course = {
            "course_name": data.get("courseName"),
            "subject_name": data.get("subjectName"),
            "class_name": data.get("className"),
            "course_date": datetime.strptime(course_date, "%Y-%m-%d").date() if course_date else None,
            "start_time": start_time,
            "end_time": end_time,
            "order_num": data.get("orderNum", inferred_order if inferred_order is not None else 0),
            "status": data.get("status", "0"),
            "create_by": "admin",
        }
        await CourseDao.add_course(db, course)
        await db.commit()

    @classmethod
    async def update_course(cls, db: AsyncSession, data: dict):
        """修改课程"""
        if not cls.is_valid_course_name(data.get("courseName")):
            raise ValueError("课节格式必须为：第X节（例如：第1节、第11节）")

        inferred_start_s, inferred_end_s, inferred_order = cls.infer_period_time_str(data.get("courseName"))
        course_date = data.get("courseDate")
        start_time = cls._parse_time_str(data.get("startTime")) or cls._parse_time_str(inferred_start_s)
        end_time = cls._parse_time_str(data.get("endTime")) or cls._parse_time_str(inferred_end_s)

        if cls.is_invalid_time_range(start_time, end_time):
            raise ValueError("课节开始时间不能晚于结束时间")

        course = {
            "course_id": data.get("courseId"),
            "course_name": data.get("courseName"),
            "subject_name": data.get("subjectName"),
            "class_name": data.get("className"),
            "course_date": datetime.strptime(course_date, "%Y-%m-%d").date() if course_date else None,
            "start_time": start_time,
            "end_time": end_time,
            "order_num": data.get("orderNum", inferred_order if inferred_order is not None else 0),
            "status": data.get("status"),
            "update_by": "admin",
        }
        await CourseDao.update_course(db, course)
        await db.commit()

    @classmethod
    async def delete_course(cls, db: AsyncSession, course_ids: str):
        """删除课程"""
        ids = [int(id) for id in course_ids.split(",")]
        await CourseDao.delete_course(db, ids)
        await db.commit()
