import math
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import (
    String,
    cast,
    distinct,
    func,
    or_,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.class_student_do import SysClassStudent
from module_camera.dao.emotion_anxiety_mapping_dao import EmotionAnxietyMappingDao
from module_camera.entity.do.course_do import SysCourse
from module_camera.entity.do.emotion_result_do import EmotionAnalysisResult
from module_camera.service.semester_service import SemesterService
from utils.common_util import CamelCaseUtil
from utils.page_util import PageResponseModel, PageUtil


class EmotionResultDao:
    """情绪识别数据访问层 - 对应 sys_emotion_result 表"""

    # ======================
    # 内部工具方法
    # ======================

    @staticmethod
    async def _get_semester_time_range(
        db: AsyncSession,
        semester_id: Optional[str],
        week_num: Optional[int],
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """根据学期ID和周次获取时间范围"""
        if week_num is not None:
            try:
                week_num = int(week_num)
            except (TypeError, ValueError):
                week_num = None

        if semester_id and week_num is not None:
            return await SemesterService.get_week_date_range(db, semester_id, week_num)
        elif semester_id:
            return await SemesterService.get_semester_date_range(db, semester_id)
        return None, None

    @staticmethod
    def _apply_time_filter(query, model, begin_time: Optional[str], end_time: Optional[str]):
        """通用时间过滤器（支持字符串日期）"""
        if begin_time:
            bt = datetime.strptime(begin_time[:10], "%Y-%m-%d")
            query = query.where(model.create_time >= bt)
        if end_time:
            et = datetime.strptime(end_time[:10], "%Y-%m-%d") + timedelta(days=1)
            query = query.where(model.create_time < et)
        return query

    # ======================
    # 主要业务方法
    # ======================

    @classmethod
    async def get_emotion_list(cls, db: AsyncSession, query_params: Dict[str, Any], is_page: bool = True):
        """获取情绪识别结果列表"""
        query = select(EmotionAnalysisResult, SysClassStudent.classes.label("class_name"))

        # 关联学生班级信息
        query = query.join(
            SysClassStudent,
            (EmotionAnalysisResult.student_id == SysClassStudent.student_id) & (SysClassStudent.del_flag == "0"),
            isouter=True,
        )

        # 班级筛选
        if class_name := query_params.get("class_name"):
            query = query.where(SysClassStudent.classes.like(f"%{class_name}%"))

        # 应用查询过滤条件
        if name := query_params.get("name"):
            query = query.where(EmotionAnalysisResult.student_name.like(f"%{name}%"))
        # 学号模糊 / 精确（统一按 like 处理，兼容“关键词输入”和“下拉选择”）
        if student := query_params.get("student"):
            query = query.where(cast(EmotionAnalysisResult.student_id, String).like(f"%{student}%"))
        # 关键词搜索：姓名 or 学号
        if keyword := query_params.get("keyword"):
            kw = str(keyword).strip()
            if kw:
                query = query.where(
                    or_(
                        EmotionAnalysisResult.student_name.like(f"%{kw}%"),
                        cast(EmotionAnalysisResult.student_id, String).like(f"%{kw}%"),
                    )
                )

        if emotion := query_params.get("emotion"):
            query = query.where(EmotionAnalysisResult.emotion == emotion)
        if camera_ip := query_params.get("camera_ip"):
            query = query.where(EmotionAnalysisResult.camera_ip == camera_ip)

        # 时间范围筛选
        query = cls._apply_time_filter(
            query, EmotionAnalysisResult, query_params.get("begin_time"), query_params.get("end_time")
        )

        query = query.order_by(EmotionAnalysisResult.create_time.desc())

        if is_page:
            page_num = int(query_params.get("page_num", 1))
            page_size = int(query_params.get("page_size", 10))
            
            # 计算总数
            total = (await db.execute(select(func.count("*")).select_from(query.subquery()))).scalar()
            
            # 分页查询
            query = query.offset((page_num - 1) * page_size).limit(page_size)
            result = await db.execute(query)
            rows = result.all()
            
            transformed_rows = []
            for emotion_obj, class_name_val in rows:
                item = CamelCaseUtil.transform_result(emotion_obj)
                if item:
                    item["className"] = class_name_val
                    transformed_rows.append(item)
            
            has_next = math.ceil(total / page_size) > page_num
            return PageResponseModel(
                rows=transformed_rows,
                pageNum=page_num,
                pageSize=page_size,
                total=total,
                hasNext=has_next,
            )
        else:
            result = await db.execute(query)
            rows = result.all()
            transformed_rows = []
            for emotion_obj, class_name_val in rows:
                item = CamelCaseUtil.transform_result(emotion_obj)
                if item:
                    item["className"] = class_name_val
                    transformed_rows.append(item)
            return transformed_rows

    @classmethod
    async def get_emotion_by_id(cls, db: AsyncSession, emotion_id: int):
        result = await db.execute(select(EmotionAnalysisResult).where(EmotionAnalysisResult.result_id == emotion_id))
        return result.scalar_one_or_none()

    @classmethod
    async def add_emotion(cls, db: AsyncSession, emotion: EmotionAnalysisResult):
        db.add(emotion)
        await db.commit()
        await db.refresh(emotion)
        return emotion

    @classmethod
    async def delete_emotion(cls, db: AsyncSession, emotion_id: int):
        """删除情绪识别结果"""
        query = select(EmotionAnalysisResult).where(EmotionAnalysisResult.result_id == emotion_id)
        result = await db.execute(query)
        emotion = result.scalar_one_or_none()
        if emotion:
            await db.delete(emotion)
            await db.commit()
            return True
        return False

    @classmethod
    async def get_user_list(cls, db: AsyncSession):
        """获取用户列表（用于下拉选择，去重）"""
        # 注意：这里可能需要根据新表结构调整，假设仍有 student_name
        query = select(distinct(EmotionAnalysisResult.student_name)).where(
            EmotionAnalysisResult.student_name.isnot(None)
        )
        result = await db.execute(query)
        return [r[0] for r in result.all() if r[0]]

    @classmethod
    async def get_user_emotion_chart(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """获取用户情绪统计图表数据"""
        # 假设统计每种情绪的数量
        query = select(
            EmotionAnalysisResult.student_name,
            EmotionAnalysisResult.emotion,
            func.count(EmotionAnalysisResult.result_id).label("count"),
        ).group_by(EmotionAnalysisResult.student_name, EmotionAnalysisResult.emotion)
        query = cls._apply_time_filter(
            query, EmotionAnalysisResult, query_params.get("begin_time"), query_params.get("end_time")
        )
        result = await db.execute(query)
        return result.all()

    @classmethod
    async def get_address_emotion_chart(cls, db: AsyncSession, query_params: Dict[str, Any]):
        query = select(
            EmotionAnalysisResult.camera_ip, func.count(EmotionAnalysisResult.result_id).label("count")
        ).group_by(EmotionAnalysisResult.camera_ip)
        query = cls._apply_time_filter(
            query, EmotionAnalysisResult, query_params.get("begin_time"), query_params.get("end_time")
        )
        result = await db.execute(query)
        return result.all()

    @classmethod
    async def get_student_emotion_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """学生情绪状态统计（柱状图）- 返回焦虑等级统计"""
        student_name = query_params.get("student_name")
        student_id = query_params.get("student_id")

        query = select(EmotionAnalysisResult.emotion)

        if student_id:
            query = query.where(EmotionAnalysisResult.student_id == student_id)
        elif student_name:
            query = query.where(EmotionAnalysisResult.student_name == student_name)

        # 学期/周过滤
        semester_id = query_params.get("semester_id")
        week_num = query_params.get("week_num")
        start, end = await cls._get_semester_time_range(db, semester_id, week_num)
        if start and end:
            query = query.where(EmotionAnalysisResult.create_time.between(start, end))

        result = await db.execute(query)
        emotions = result.scalars().all()

        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)
        anxiety_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        anxiety_names = {0: "无焦虑", 1: "低度焦虑", 2: "中度焦虑", 3: "高度焦虑"}

        for emotion in emotions:
            if not emotion:
                continue
            level = mapping_dict.get(emotion.lower(), 0)
            anxiety_counts[level] += 1

        anxiety_stats = []
        for level in [0, 1, 2, 3]:
            anxiety_stats.append({"name": anxiety_names[level], "count": anxiety_counts[level]})

        return {"anxietyStats": anxiety_stats}

    @classmethod
    async def get_subject_emotion_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """学生各科目情绪分布（堆叠柱状图）"""
        # 获取所有科目
        subjects = ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]

        # 获取课程时间表映射 (class_name, date) -> [(start, end, subject)]
        # 简化处理：假设 query_params 必须包含 student_name 以确定班级
        # 但 EmotionAnalysisResult 没有 class_name，需关联 SysClassStudent

        # 1. 查出该学生的所有情绪记录及班级
        query = (
            select(EmotionAnalysisResult, SysClassStudent.classes)
            .join(SysClassStudent, EmotionAnalysisResult.student_id == SysClassStudent.student_id)
            .where((SysClassStudent.classes != "") & (SysClassStudent.del_flag == "0"))
        )

        if search := query_params.get("student_name"):
            if search.isdigit():
                query = query.where(EmotionAnalysisResult.student_id == search)
            else:
                query = query.where(EmotionAnalysisResult.student_name.like(f"%{search}%"))
        if student_id := query_params.get("student_id"):
            query = query.where(EmotionAnalysisResult.student_id == student_id)
        if class_name := query_params.get("class_name"):
            query = query.where(SysClassStudent.classes.like(f"%{class_name}%"))

        # 学期/周过滤
        semester_id = query_params.get("semester_id")
        week_num = query_params.get("week_num")
        start, end = await cls._get_semester_time_range(db, semester_id, week_num)
        if start and end:
            query = query.where(EmotionAnalysisResult.create_time.between(start, end))

        records = (await db.execute(query)).fetchall()
        if not records:
            return {"subjects": subjects, "data": {s: {0: 0, 1: 0, 2: 0, 3: 0} for s in subjects}}

        emotion_to_anxiety = await EmotionAnxietyMappingDao.get_mapping_dict(db)
        subject_stats = {s: {0: 0, 1: 0, 2: 0, 3: 0} for s in subjects}

        # 2. 获取课程表数据以构建映射
        course_query = select(SysCourse)

        # 时间范围过滤
        if start and end:
            course_query = course_query.where(SysCourse.course_date.between(start.date(), end.date()))

        # 班级过滤
        involved_classes = set(r[1] for r in records if r[1])
        if involved_classes:
            course_query = course_query.where(SysCourse.class_name.in_(involved_classes))

        courses = (await db.execute(course_query)).scalars().all()

        # 构建查找表: class -> date -> [(start_time, end_time, subject)]
        schedule_map = {}
        for c in courses:
            if not c.class_name or not c.course_date or not c.start_time or not c.end_time:
                continue
            if c.class_name not in schedule_map:
                schedule_map[c.class_name] = {}
            if c.course_date not in schedule_map[c.class_name]:
                schedule_map[c.class_name][c.course_date] = []
            schedule_map[c.class_name][c.course_date].append((c.start_time, c.end_time, c.subject_name))

        # 3. 匹配情绪记录到科目
        for emotion_rec, class_name in records:
            if not emotion_rec.create_time or not class_name:
                continue

            rec_date = emotion_rec.create_time.date()
            rec_time = emotion_rec.create_time.time()

            if class_name in schedule_map and rec_date in schedule_map[class_name]:
                for start_t, end_t, subj in schedule_map[class_name][rec_date]:
                    # 注意：start_t 和 end_t 可能是 time 对象
                    if start_t <= rec_time <= end_t:
                        # 找到对应科目
                        if subj in subject_stats:
                            level = emotion_to_anxiety.get(emotion_rec.emotion.lower(), 0)
                            subject_stats[subj][level] += 1
                        break

        return {"subjects": subjects, "data": subject_stats}

    @classmethod
    async def get_class_anxiety_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """班级学生焦虑类型总人次数分布"""
        # 1. 过滤条件
        class_name = query_params.get("class_name")
        semester_id = query_params.get("semester_id")
        week_num = query_params.get("week_num")

        query = select(EmotionAnalysisResult.emotion)

        if class_name:
            query = query.join(
                SysClassStudent,
                (EmotionAnalysisResult.student_id == SysClassStudent.student_id) & (SysClassStudent.del_flag == "0"),
                isouter=False,
            ).where(SysClassStudent.classes.like(f"%{class_name}%"))

        start, end = await cls._get_semester_time_range(db, semester_id, week_num)
        if start and end:
            query = query.where(EmotionAnalysisResult.create_time.between(start, end))

        result = await db.execute(query)
        emotions = result.scalars().all()

        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)
        anxiety_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        anxiety_names = {0: "无焦虑", 1: "低度焦虑", 2: "中度焦虑", 3: "高度焦虑"}

        for emotion in emotions:
            if not emotion:
                continue
            level = mapping_dict.get(emotion.lower(), 0)
            anxiety_counts[level] += 1

        data_list = []
        for level in [0, 1, 2, 3]:
            data_list.append(
                {
                    "name": anxiety_names[level],
                    "value": anxiety_counts[level],
                    "count": anxiety_counts[level],  # 兼容前端字段
                    "level": level,
                }
            )

        return data_list

    @classmethod
    async def get_class_subject_anxiety_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """班级学生各科目焦虑人次数分布"""
        from collections import defaultdict

        # 1. 获取过滤条件
        class_name = query_params.get("class_name")
        semester_id = query_params.get("semester_id")
        week_num = query_params.get("week_num")

        # 2. 获取时间范围
        start, end = await cls._get_semester_time_range(db, semester_id, week_num)

        # 3. 查询该班级在该时间段内的所有课程
        course_query = select(SysCourse).where(SysCourse.class_name == class_name)
        if start and end:
            # SysCourse.course_date is Date, so comparison works
            course_query = course_query.where(SysCourse.course_date.between(start.date(), end.date()))

        course_result = await db.execute(course_query)
        courses = course_result.scalars().all()

        # 构建课程时间表索引: {subject: [(date, start, end), ...]}
        subject_schedule = defaultdict(list)
        for course in courses:
            if course.subject_name:
                subject_schedule[course.subject_name].append((course.course_date, course.start_time, course.end_time))

        # 4. 查询该班级在该时间段内的所有情绪记录
        emotion_query = (
            select(EmotionAnalysisResult.emotion, EmotionAnalysisResult.create_time)
            .join(SysClassStudent, EmotionAnalysisResult.student_id == SysClassStudent.student_id)
            .where(SysClassStudent.classes == class_name)
        )

        if start and end:
            emotion_query = emotion_query.where(EmotionAnalysisResult.create_time.between(start, end))

        emotion_result = await db.execute(emotion_query)
        emotions = emotion_result.all()

        # 5. 统计各科目焦虑分布
        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)
        # 初始化统计结果
        subjects = ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"]
        stats = {s: {0: 0, 1: 0, 2: 0, 3: 0} for s in subjects}

        for emotion_str, create_time in emotions:
            level = mapping_dict.get(emotion_str.lower(), 0)
            e_date = create_time.date()
            e_time = create_time.time()

            # 查找所属科目
            matched_subject = None

            # 遍历所有科目查找匹配的时间段
            # 优先匹配 subjects 列表中的科目
            for subj in subjects:
                for c_date, c_start, c_end in subject_schedule.get(subj, []):
                    if c_date == e_date and c_start <= e_time <= c_end:
                        matched_subject = subj
                        break
                if matched_subject:
                    break

            if matched_subject:
                stats[matched_subject][level] += 1

        # 6. 格式化返回数据
        return {
            "subjects": subjects,
            "no_anxiety": [stats[s][0] for s in subjects],
            "low_anxiety": [stats[s][1] for s in subjects],
            "mid_anxiety": [stats[s][2] for s in subjects],
            "high_anxiety": [stats[s][3] for s in subjects],
        }

    @classmethod
    async def get_class_emotion_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """班级情绪状态统计"""
        # ... 实现逻辑类似，注意字段名变更 ...
        return {}

    @classmethod
    async def get_weekly_emotion_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """学生每周情绪状态统计"""
        # ... 实现逻辑类似 ...
        return {}

    @classmethod
    async def get_all_weeks_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """学生各周情绪状态（折线图）"""
        return await cls.get_semester_weeks_stats(db, query_params)

    @classmethod
    async def get_semester_weeks_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """
        获取学期各周情绪统计（柱状图数据）
        返回: {
            "weeks": ["第1周", "第2周", ...],
            "noAnxiety": [10, 12, ...],
            "lowAnxiety": [5, 3, ...],
            "midAnxiety": [2, 1, ...],
            "highAnxiety": [0, 0, ...]
        }
        """
        semester_id = query_params.get("semester_id")
        if not semester_id:
            # 获取当前学期
            current_semester = await SemesterService.get_current_semester(db)
            semester_id = current_semester.get("id") if current_semester else None

        if not semester_id:
            return {"weeks": [], "noAnxiety": [], "lowAnxiety": [], "midAnxiety": [], "highAnxiety": []}

        # 获取该学期的所有周次
        semester_weeks = await SemesterService.get_semester_weeks(db, semester_id)

        weeks_label = []
        data = {"noAnxiety": [], "lowAnxiety": [], "midAnxiety": [], "highAnxiety": []}

        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)

        # 遍历每一周统计数据
        for week_info in semester_weeks:
            week_num = week_info.get("weekNum")
            week_name = week_info.get("name")
            weeks_label.append(week_name)

            # 获取该周的时间范围
            start_dt, end_dt = await SemesterService.get_week_date_range(db, semester_id, week_num)

            # 统计该时间段内的情绪数据
            anxiety_counts = {0: 0, 1: 0, 2: 0, 3: 0}
            if start_dt and end_dt:
                query = select(EmotionAnalysisResult.emotion).where(
                    EmotionAnalysisResult.create_time.between(start_dt, end_dt)
                )

                if student_id := query_params.get("student_id"):
                    query = query.where(EmotionAnalysisResult.student_id == student_id)
                elif student_name := query_params.get("student_name"):
                    query = query.where(EmotionAnalysisResult.student_name == student_name)

                result = await db.execute(query)
                emotions = result.scalars().all()

                for emotion in emotions:
                    if not emotion:
                        continue
                    level = mapping_dict.get(emotion.lower(), 0)
                    anxiety_counts[level] += 1

            data["noAnxiety"].append(anxiety_counts[0])
            data["lowAnxiety"].append(anxiety_counts[1])
            data["midAnxiety"].append(anxiety_counts[2])
            data["highAnxiety"].append(anxiety_counts[3])

        return {"weeks": weeks_label, **data}

    @classmethod
    async def get_semester_week_detail_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """获取指定周的详细统计"""
        semester_id = query_params.get("semester_id")
        week_num = query_params.get("week_num")

        if not semester_id or not week_num:
            return {}

        try:
            week_num = int(week_num)
        except (ValueError, TypeError):
            return {}

        start_dt, end_dt = await SemesterService.get_week_date_range(db, semester_id, week_num)
        if not start_dt or not end_dt:
            return {}

        # Prepare days list (Mon, Tue, ..., Sun)
        days_label = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)
        
        data = {
            "days": days_label,
            "startDate": start_dt.strftime("%Y-%m-%d"),
            "endDate": end_dt.strftime("%Y-%m-%d"),
            "noAnxiety": [0]*7,
            "lowAnxiety": [0]*7,
            "midAnxiety": [0]*7,
            "highAnxiety": [0]*7
        }

        # Query all data for this week
        query = select(
            func.date(EmotionAnalysisResult.create_time).label("date"), 
            EmotionAnalysisResult.emotion
        ).where(
            EmotionAnalysisResult.create_time >= start_dt,
            EmotionAnalysisResult.create_time <= end_dt
        )
        
        result = await db.execute(query)
        rows = result.all()
        
        # Aggregate
        start_date_obj = start_dt.date()
        for row in rows:
            date_val = row.date
            emotion = row.emotion
            if not emotion: 
                continue
                
            # Find index (0-6)
            # date_val might be string or date object depending on driver/dialect, ensure it's comparable
            if isinstance(date_val, str):
                date_val = datetime.strptime(date_val, "%Y-%m-%d").date()
            
            day_diff = (date_val - start_date_obj).days
            if 0 <= day_diff < 7:
                level = mapping_dict.get(emotion.lower(), 0)
                if level == 0: data["noAnxiety"][day_diff] += 1
                elif level == 1: data["lowAnxiety"][day_diff] += 1
                elif level == 2: data["midAnxiety"][day_diff] += 1
                elif level == 3: data["highAnxiety"][day_diff] += 1
                
        return data

    @classmethod
    async def get_dashboard_overall_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """
        首页总体趋势图 (最近7天)
        返回格式: {
            "dates": ["MM-DD", ...],
            "noAnxiety": [num, ...],
            "lowAnxiety": [num, ...],
            "midAnxiety": [num, ...],
            "highAnxiety": [num, ...]
        }
        """
        # 1. 确定日期范围（最近7天）
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]  # [today-6, ..., today]
        date_strs = [d.strftime("%Y-%m-%d") for d in dates]
        chart_dates = [d.strftime("%Y-%m-%d") for d in dates]

        # 2. 获取映射字典
        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)

        # 3. 查询这7天的数据
        start_date = dates[0]
        end_date = dates[-1] + timedelta(days=1)

        query = select(
            func.date_format(EmotionAnalysisResult.create_time, "%Y-%m-%d").label("date"), EmotionAnalysisResult.emotion
        ).where(EmotionAnalysisResult.create_time >= start_date, EmotionAnalysisResult.create_time < end_date)

        # 学生ID筛选
        if student_id := query_params.get("student_id"):
            query = query.where(EmotionAnalysisResult.student_id == student_id)

        result = await db.execute(query)
        rows = result.all()

        # 4. 统计数据
        # 结构: { '2023-01-01': {0: count, 1: count, ...} }
        stats = {d: {0: 0, 1: 0, 2: 0, 3: 0} for d in date_strs}

        for row in rows:
            date_str = row[0]
            emotion = row[1]
            if date_str in stats and emotion:
                level = mapping_dict.get(emotion.lower(), 0)
                stats[date_str][level] += 1

        # 5. 组装返回结果
        return {
            "dates": chart_dates,
            "noAnxiety": [stats[d][0] for d in date_strs],
            "lowAnxiety": [stats[d][1] for d in date_strs],
            "midAnxiety": [stats[d][2] for d in date_strs],
            "highAnxiety": [stats[d][3] for d in date_strs],
        }

    @classmethod
    async def get_dashboard_trend_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """
        首页焦虑趋势统计 (饼图)
        返回格式: { "total": 总数, "data": [{"name": "焦虑类型", "value": 数量}, ...] }
        """
        # 1. 获取情绪到焦虑等级的映射
        mapping_dict = await EmotionAnxietyMappingDao.get_mapping_dict(db)

        # 2. 查询时间范围内的所有情绪记录
        query = select(EmotionAnalysisResult.emotion)
        query = cls._apply_time_filter(
            query, EmotionAnalysisResult, query_params.get("begin_time"), query_params.get("end_time")
        )

        result = await db.execute(query)
        emotions = result.scalars().all()

        # 3. 统计各焦虑等级数量
        # 0:无焦虑, 1:低度焦虑, 2:中度焦虑, 3:高度焦虑
        anxiety_counts = {0: 0, 1: 0, 2: 0, 3: 0}
        anxiety_names = {0: "无焦虑", 1: "低度焦虑", 2: "中度焦虑", 3: "高度焦虑"}

        for emotion in emotions:
            if not emotion:
                continue
            # 统一转小写匹配
            level = mapping_dict.get(emotion.lower(), 0)  # 默认无焦虑
            anxiety_counts[level] += 1

        # 4. 构造返回数据
        data_list = []
        total_count = len(emotions)

        # 按顺序 0-3 添加到列表 (或者只返回有数据的)
        # 前端代码 colors 对应 0-3 的顺序 ["#457244", "#00cc99", "#ffcc66", "#ff4d4d"]
        # 所以必须按 0,1,2,3 的顺序返回
        for level in [0, 1, 2, 3]:
            data_list.append({"name": anxiety_names[level], "value": anxiety_counts[level]})

        return {"total": total_count, "data": data_list}

    @classmethod
    async def get_dashboard_mood_stats(cls, db: AsyncSession, query_params: Dict[str, Any]):
        """首页情绪分布饼图"""
        query = select(EmotionAnalysisResult.emotion, func.count(EmotionAnalysisResult.result_id).label("count"))
        query = cls._apply_time_filter(
            query, EmotionAnalysisResult, query_params.get("begin_time"), query_params.get("end_time")
        )
        query = query.group_by(EmotionAnalysisResult.emotion)
        result = await db.execute(query)

        data_list = [{"name": r[0], "value": r[1]} for r in result.all()]
        # 前端期望: { data: [...] } 或直接 [...]
        # 但根据 index.vue:203 this.renderMoodChart -> this.moodData.data.map
        # 所以必须返回包含 data 字段的对象
        return {"data": data_list}

    @classmethod
    async def get_unknown_list(cls, db: AsyncSession, query_params: Dict[str, Any], is_page: bool = True):
        """获取陌生人员（无学号/姓名）列表"""
        query = select(EmotionAnalysisResult).where(
            or_(
                EmotionAnalysisResult.student_id.is_(None),
                EmotionAnalysisResult.student_id == "",
                EmotionAnalysisResult.student_name.is_(None),
                EmotionAnalysisResult.student_name == "Unknown",
            )
        )
        query = cls._apply_time_filter(
            query, EmotionAnalysisResult, query_params.get("begin_time"), query_params.get("end_time")
        )
        query = query.order_by(EmotionAnalysisResult.create_time.desc())

        if is_page:
            page_num = int(query_params.get("page_num", 1))
            page_size = int(query_params.get("page_size", 10))
            return await PageUtil.paginate(db, query, page_num, page_size, is_page=True)
        return (await db.execute(query)).scalars().all()
