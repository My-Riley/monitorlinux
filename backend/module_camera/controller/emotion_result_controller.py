import base64
import io
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from openpyxl.drawing.image import Image as ExcelImage
from openpyxl.utils import get_column_letter
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.service.login_service import LoginService
from module_camera.service.emotion_result_service import EmotionResultService
from utils.log_util import logger
from utils.response_util import ResponseUtil

emotionController = APIRouter(prefix="/system/results", dependencies=[Depends(LoginService.get_current_user)])


@emotionController.get("/list")
async def get_emotion_list(
    request: Request,
    name: Optional[str] = Query(default=None, alias="studentName"),  # 兼容前端
    student: Optional[str] = Query(default=None, alias="studentId"),
    keyword: Optional[str] = Query(default=None),
    class_name: Optional[str] = Query(default=None, alias="className"),
    course_id: Optional[int] = Query(default=None, alias="courseId"),
    emotion: Optional[str] = Query(default=None),
    camera_ip: Optional[str] = Query(default=None, alias="cameraIp"),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取情绪识别结果列表"""
    # 兼容旧参数
    if not name:
        name = request.query_params.get("name")
    if not student:
        student = request.query_params.get("Student") or request.query_params.get("student")

    query_params = {
        "name": name,
        "student": student,
        "keyword": keyword,
        "class_name": class_name,
        "course_id": course_id,
        "emotion": emotion,
        "camera_ip": camera_ip,
        "begin_time": begin_time,
        "end_time": end_time,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await EmotionResultService.get_emotion_list(query_db, query_params, is_page=True)
    logger.info("获取情绪识别结果列表成功")
    return ResponseUtil.success(model_content=result)


@emotionController.get("/export")
async def export_emotion_list(
    request: Request,
    name: Optional[str] = Query(default=None, alias="studentName"),
    student: Optional[str] = Query(default=None, alias="studentId"),
    keyword: Optional[str] = Query(default=None),
    class_name: Optional[str] = Query(default=None, alias="className"),
    course_id: Optional[int] = Query(default=None, alias="courseId"),
    emotion: Optional[str] = Query(default=None),
    camera_ip: Optional[str] = Query(default=None, alias="cameraIp"),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """导出情绪识别结果列表"""
    # 兼容
    if not name:
        name = request.query_params.get("name")
    if not student:
        student = request.query_params.get("Student")

    query_params = {
        "name": name,
        "student": student,
        "keyword": keyword,
        "class_name": class_name,
        "course_id": course_id,
        "emotion": emotion,
        "camera_ip": camera_ip,
        "begin_time": begin_time,
        "end_time": end_time,
        "page_num": 1,
        "page_size": 100000,
    }
    result = await EmotionResultService.get_emotion_list(query_db, query_params, is_page=False)

    if not result:
        return ResponseUtil.error(msg="暂无数据可导出")

    export_data = []
    emotion_labels = {
        "neutral": "中性",
        "happiness": "喜悦",
        "surprise": "惊讶",
        "sadness": "悲伤",
        "anger": "愤怒",
        "disgust": "厌恶",
        "fear": "恐惧",
        "contempt": "藐视",
        "unknown": "未知",
    }

    for item in result:
        # item is dict (camelCase from CamelCaseUtil)
        export_data.append(
            {
                "姓名": item.get("studentName", item.get("name", "")),
                "学号": item.get("studentId", item.get("Student", "")),
                "班级": item.get("className", ""),
                "设备ID号": str(item.get("cameraIp", "")).replace(" ", ""),
                "情绪": emotion_labels.get(item.get("emotion"), item.get("emotion") or "未知"),
                '抓拍人脸图片': '',  # 图片占位符
                "检测时间": item.get("createTime", item.get("timestamp")),  # datetime obj
            }
        )

    output = io.BytesIO()
    df = pd.DataFrame(export_data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="检测记录")
        worksheet = writer.sheets["检测记录"]

        # 调整列宽
        for idx, col in enumerate(df.columns, 1):
            worksheet.column_dimensions[get_column_letter(idx)].width = 25

        # 图片列需要更宽一点（F列是抓拍人脸图片）
        worksheet.column_dimensions["F"].width = 15

        # 插入图片到 F 列（抓拍人脸图片）
        for idx, item in enumerate(result, start=2):  # openpyxl 行号从1开始，表头占一行
            image_base64 = item.get("imageBase64")
            if image_base64:
                try:
                    # 处理 base64 前缀
                    if "," in image_base64:
                        image_base64 = image_base64.split(",")[1]

                    img_data = base64.b64decode(image_base64)
                    image_stream = io.BytesIO(img_data)
                    img = ExcelImage(image_stream)

                    # 调整图片大小以适应单元格
                    img.width = 100
                    img.height = 100

                    cell_address = f"F{idx}"
                    worksheet.add_image(img, cell_address)

                    # 调整行高以适应图片
                    worksheet.row_dimensions[idx].height = 80
                except Exception as e:
                    logger.error(f"导出图片失败 (row {idx}): {e}")

    output.seek(0)
    logger.info("导出情绪识别结果列表成功")

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=emotion_records.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )


@emotionController.get("/listFocus")
async def get_focus_list(
    request: Request,
    name: Optional[str] = Query(default=None, alias="imageName"),
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取重点关注人员列表"""
    query_params = {
        "name": name,
        "begin_time": begin_time,
        "end_time": end_time,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await EmotionResultService.get_focus_list(query_db, query_params, is_page=True)
    logger.info("获取重点关注人员列表成功")
    return ResponseUtil.success(dict_content=result)


@emotionController.get("/listUnknown")
async def get_unknown_list(
    request: Request,
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取陌生人员列表"""
    query_params = {
        "begin_time": begin_time,
        "end_time": end_time,
        "page_num": page_num,
        "page_size": page_size,
    }
    result = await EmotionResultService.get_unknown_list(query_db, query_params, is_page=True)
    logger.info("获取陌生人员列表成功")
    return ResponseUtil.success(dict_content=result)


@emotionController.get("/listAddressChart")
async def get_address_emotion_chart(
    request: Request,
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取地点情绪统计图表数据"""
    query_params = {
        "begin_time": begin_time,
        "end_time": end_time,
    }
    result = await EmotionResultService.get_address_emotion_chart(query_db, query_params)
    chart_data = [{"cameraIp": r[0], "count": r[1]} for r in result]
    logger.info("获取地点情绪统计图表数据成功")
    return ResponseUtil.success(data=chart_data)


@emotionController.get("/dashboard/overall")
async def get_dashboard_overall(
    request: Request,
    studentId: str = None,
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取首页总体趋势图数据"""
    query_params = {
        "begin_time": begin_time,
        "end_time": end_time,
    }
    if studentId:
        query_params["student_id"] = studentId

    result = await EmotionResultService.get_dashboard_overall_stats(query_db, query_params)
    logger.info("获取首页总体趋势图数据成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/dashboard/trend")
async def get_dashboard_trend(
    request: Request,
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取首页焦虑趋势饼图数据"""
    query_params = {
        "begin_time": begin_time,
        "end_time": end_time,
    }
    result = await EmotionResultService.get_dashboard_trend_stats(query_db, query_params)
    logger.info("获取首页焦虑趋势饼图数据成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/dashboard/mood")
async def get_dashboard_mood(
    request: Request,
    begin_time: Optional[str] = Query(default=None, alias="beginTime"),
    end_time: Optional[str] = Query(default=None, alias="endTime"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取首页情绪分布饼图数据"""
    query_params = {
        "begin_time": begin_time,
        "end_time": end_time,
    }
    result = await EmotionResultService.get_dashboard_mood_stats(query_db, query_params)
    logger.info("获取首页情绪分布饼图数据成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/classAnxietyTypeStats")
async def get_class_anxiety_type_stats(
    request: Request,
    class_name: Optional[str] = Query(default=None, alias="className"),
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    week_num: Optional[str] = Query(default=None, alias="weekNum"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取班级学生焦虑类型总人次数分布"""
    query_params = {
        "class_name": class_name,
        "semester_id": semester_id,
        "week_num": week_num,
    }
    result = await EmotionResultService.get_class_anxiety_stats(query_db, query_params)
    logger.info("获取班级学生焦虑类型总人次数分布成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/classSubjectAnxietyStats")
async def get_class_subject_anxiety_stats(
    request: Request,
    class_name: Optional[str] = Query(default=None, alias="className"),
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    week_num: Optional[str] = Query(default=None, alias="weekNum"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取班级学生各科目焦虑人次数分布"""
    query_params = {
        "class_name": class_name,
        "semester_id": semester_id,
        "week_num": week_num,
    }
    result = await EmotionResultService.get_class_subject_anxiety_stats(query_db, query_params)
    logger.info("获取班级学生各科目焦虑人次数分布成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/studentStats")
async def get_student_stats(
    request: Request,
    student_name: Optional[str] = Query(default=None, alias="studentName"),
    student_id: Optional[str] = Query(default=None, alias="studentId"),
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    week_num: Optional[str] = Query(default=None, alias="weekNum"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学生情绪状态统计"""
    query_params = {
        "student_name": student_name,
        "student_id": student_id,
        "semester_id": semester_id,
        "week_num": week_num,
    }
    result = await EmotionResultService.get_student_emotion_stats(query_db, query_params)
    logger.info("获取学生情绪状态统计成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/subjectStats")
async def get_subject_stats(
    request: Request,
    student_name: Optional[str] = Query(default=None, alias="studentName"),
    student_id: Optional[str] = Query(default=None, alias="studentId"),
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    week_num: Optional[str] = Query(default=None, alias="weekNum"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学生各科目情绪分布"""
    query_params = {
        "student_name": student_name,
        "student_id": student_id,
        "semester_id": semester_id,
        "week_num": week_num,
    }
    result = await EmotionResultService.get_subject_emotion_stats(query_db, query_params)
    logger.info("获取学生各科目情绪分布成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/weeklyStats")
async def get_weekly_stats(
    request: Request,
    student_name: Optional[str] = Query(default=None, alias="studentName"),
    student_id: Optional[str] = Query(default=None, alias="studentId"),
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学生每周情绪状态统计"""
    query_params = {
        "student_name": student_name,
        "student_id": student_id,
        "semester_id": semester_id,
    }
    result = await EmotionResultService.get_weekly_emotion_stats(query_db, query_params)
    logger.info("获取学生每周情绪状态统计成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/allWeeksStats")
async def get_all_weeks_stats(
    request: Request,
    student_name: Optional[str] = Query(default=None, alias="studentName"),
    student_id: Optional[str] = Query(default=None, alias="studentId"),
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学生各周情绪状态（折线图）"""
    query_params = {
        "student_name": student_name,
        "student_id": student_id,
        "semester_id": semester_id,
    }
    result = await EmotionResultService.get_all_weeks_stats(query_db, query_params)
    logger.info("获取学生各周情绪状态成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/semesterWeeks")
async def get_semester_weeks_stats(
    request: Request,
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学期各周情绪统计"""
    query_params = {"semester_id": semester_id}
    result = await EmotionResultService.get_semester_weeks_stats(query_db, query_params)
    logger.info("获取学期各周情绪统计成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/semesterWeekStats")
async def get_semester_week_detail_stats(
    request: Request,
    semester_id: Optional[str] = Query(default=None, alias="semesterId"),
    week_num: Optional[int] = Query(default=None, alias="weekNum"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学期指定周的详细统计"""
    query_params = {"semester_id": semester_id, "week_num": week_num}
    result = await EmotionResultService.get_semester_week_detail_stats(query_db, query_params)
    logger.info("获取学期指定周详细统计成功")
    return ResponseUtil.success(data=result)


@emotionController.get("/{emotion_id}")
async def get_emotion_detail(
    request: Request,
    emotion_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取情绪识别结果详情"""
    result = await EmotionResultService.get_emotion_by_id(query_db, emotion_id)
    from utils.common_util import CamelCaseUtil

    logger.info("获取情绪识别结果详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(result))


@emotionController.delete("/{ids}")
async def delete_emotion(
    request: Request,
    ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """批量删除情绪识别结果"""
    # 这里的 ids 约定为逗号分隔的 ID 字符串
    id_list = [int(x.strip()) for x in ids.split(",") if x.strip()]
    if not id_list:
        return ResponseUtil.error(msg="无效的ID")

    for emotion_id in id_list:
        await EmotionResultService.delete_emotion(query_db, emotion_id)
    
    logger.info(f"成功删除 {len(id_list)} 条情绪识别结果")
    return ResponseUtil.success(msg=f"成功删除 {len(id_list)} 条数据")
