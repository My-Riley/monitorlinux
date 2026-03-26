"""
课程导入控制器
支持Excel文件批量导入课程数据
"""

import io
import re
from datetime import date, datetime, time
from typing import Any, List

import pandas as pd
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.user_class_service import UserClassService
from module_camera.dao.course_dao import CourseDao
from module_camera.entity.do.course_do import SysCourse
from utils.log_util import logger
from utils.response_util import ResponseUtil

courseImportController = APIRouter(
    prefix="/cell/course", dependencies=[Depends(LoginService.get_current_user)], tags=["课程导入"]
)


def _validate_course_name(course_name: str) -> tuple[bool, str]:
    """验证课节名称"""
    if not course_name:
        return False, "课节名称不能为空"
    s = str(course_name).strip()
    if not re.fullmatch(r"第[0-9一二三四五六七八九十百零〇两]+节", s):
        return False, "课节格式必须为：第X节（例如：第1节、第11节）"
    return True, ""


def _validate_class_name(class_name: str) -> tuple[bool, str]:
    if not class_name:
        return False, "班级不能为空"
    s = str(class_name).strip()
    if not re.fullmatch(r"\d{4}班", s):
        return False, "班级格式必须为：前四位数字+班（例如：2024班）"
    return True, ""


def _validate_class_existence(class_name: str, system_classes: set[str]) -> tuple[bool, str]:
    if class_name not in system_classes:
        return False, "该班级不存在于系统班级列表中"
    return True, ""


def _validate_date(value: Any) -> tuple[bool, str, Any]:
    """验证日期格式"""
    if value is None:
        return False, "日期不能为空", None

    if isinstance(value, float) and pd.isna(value):
        return False, "日期不能为空", None

    if isinstance(value, date) and not isinstance(value, datetime):
        return True, "", value

    if isinstance(value, datetime):
        return True, "", value.date()

    if hasattr(value, "to_pydatetime"):
        try:
            dt = value.to_pydatetime()
            if isinstance(dt, datetime):
                return True, "", dt.date()
        except Exception:
            pass

    date_str = str(value).strip()
    if not date_str or date_str.lower() == "nan":
        return False, "日期不能为空", None

    m = re.match(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})", date_str)
    if m:
        try:
            return (
                True,
                "",
                datetime.strptime(f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}", "%Y-%m-%d").date(),
            )
        except Exception:
            pass

    try:
        # 尝试多种日期格式
        for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"]:
            try:
                date_obj = datetime.strptime(date_str, fmt).date()
                return True, "", date_obj
            except ValueError:
                continue
        return False, "日期格式错误，应为：YYYY-MM-DD", None
    except Exception as e:
        return False, f"日期解析失败：{str(e)}", None


def _infer_order_num(course_name: str) -> int:
    """根据课节名称推断排序号"""
    mapping = {
        "第一节": 1,
        "第二节": 2,
        "第三节": 3,
        "第四节": 4,
        "第五节": 5,
        "第六节": 6,
        "第七节": 7,
        "第八节": 8,
        "第九节": 9,
        "第1节": 1,
        "第2节": 2,
        "第3节": 3,
        "第4节": 4,
        "第5节": 5,
        "第6节": 6,
        "第7节": 7,
        "第8节": 8,
        "第9节": 9,
    }
    return mapping.get(course_name, 0)


def _infer_period_times(course_name: str) -> tuple[Any, Any]:
    mapping = {
        "第一节": ("08:00", "08:45"),
        "第二节": ("08:55", "09:40"),
        "第三节": ("10:00", "10:45"),
        "第四节": ("10:55", "11:40"),
        "第五节": ("14:00", "14:45"),
        "第六节": ("14:55", "15:40"),
        "第七节": ("16:00", "16:45"),
        "第八节": ("16:55", "17:40"),
        "第九节": ("19:00", "19:45"),
        "第1节": ("08:00", "08:45"),
        "第2节": ("08:55", "09:40"),
        "第3节": ("10:00", "10:45"),
        "第4节": ("10:55", "11:40"),
        "第5节": ("14:00", "14:45"),
        "第6节": ("14:55", "15:40"),
        "第7节": ("16:00", "16:45"),
        "第8节": ("16:55", "17:40"),
        "第9节": ("19:00", "19:45"),
    }
    start_s, end_s = mapping.get(course_name, (None, None))
    start_t = datetime.strptime(start_s, "%H:%M").time() if start_s else None
    end_t = datetime.strptime(end_s, "%H:%M").time() if end_s else None
    return start_t, end_t


def _parse_time_cell(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, float) and pd.isna(value):
        return None

    if isinstance(value, str):
        s = value.strip()
        if not s or s.lower() == "nan":
            return None
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).time()
            except Exception:
                continue
        return None

    if isinstance(value, time):
        return value

    if isinstance(value, datetime):
        return value.time()

    if hasattr(value, "to_pydatetime"):
        try:
            return value.to_pydatetime().time()
        except Exception:
            return None

    return _parse_time_cell(str(value))


def _build_error_report_csv(errors: list[dict]) -> str:
    lines = ["行号,字段,错误,值"]
    for e in errors:

        def _clean(s: str) -> str:
            return s.replace("\r", " ").replace("\n", " ")

        row_num = _clean(str(e.get("rowNum") or ""))
        field = _clean(str(e.get("field") or ""))
        msg = _clean(str(e.get("message") or ""))
        value = _clean(str(e.get("value") or ""))

        def _csv_escape(s: str) -> str:
            if any(ch in s for ch in [",", '"', "\n", "\r"]):
                return '"' + s.replace('"', '""') + '"'
            return s

        lines.append(",".join([_csv_escape(row_num), _csv_escape(field), _csv_escape(msg), _csv_escape(value)]))
    return "\ufeff" + "\n".join(lines)


async def _precheck_course_dataframe(
    df: pd.DataFrame,
    system_classes: set[str],
    query_db: AsyncSession,
    update_support: bool = False,
) -> tuple[list[dict], list[dict]]:
    ok_rows: list[dict] = []
    errors: list[dict] = []

    for index, row in df.iterrows():
        row_num = index + 2
        try:
            course_name = str(row.get("课节", "")).strip()
            if course_name.lower() == "nan" or course_name == "":
                errors.append(
                    {"rowNum": row_num, "field": "课节", "message": "课节名称为空", "value": row.get("课节", "")}
                )
                continue

            is_valid, error_msg = _validate_course_name(course_name)
            if not is_valid:
                errors.append({"rowNum": row_num, "field": "课节", "message": error_msg, "value": row.get("课节", "")})
                continue

            subject_name = str(row.get("学科", "")).strip()
            if subject_name.lower() == "nan" or subject_name == "":
                errors.append(
                    {"rowNum": row_num, "field": "学科", "message": "学科名称为空", "value": row.get("学科", "")}
                )
                continue

            class_name = str(row.get("班级", "")).strip()
            if class_name.lower() == "nan" or class_name == "":
                errors.append({"rowNum": row_num, "field": "班级", "message": "班级为空", "value": row.get("班级", "")})
                continue

            is_valid, error_msg = _validate_class_name(class_name)
            if not is_valid:
                errors.append({"rowNum": row_num, "field": "班级", "message": error_msg, "value": row.get("班级", "")})
                continue

            is_valid, error_msg = _validate_class_existence(class_name, system_classes)
            if not is_valid:
                errors.append({"rowNum": row_num, "field": "班级", "message": error_msg, "value": row.get("班级", "")})
                continue

            is_valid, error_msg, course_date = _validate_date(row.get("日期"))
            if not is_valid:
                errors.append({"rowNum": row_num, "field": "日期", "message": error_msg, "value": row.get("日期", "")})
                continue

            inferred_start_time, inferred_end_time = _infer_period_times(course_name)
            start_time = _parse_time_cell(row.get("课节开始时间")) or inferred_start_time
            end_time = _parse_time_cell(row.get("课节结束时间")) or inferred_end_time
            if start_time and end_time and start_time > end_time:
                errors.append(
                    {
                        "rowNum": row_num,
                        "field": "课节开始时间",
                        "message": "课节开始时间不能晚于结束时间",
                        "value": row.get("课节开始时间", ""),
                    }
                )
                continue

            existing_query = select(SysCourse).where(
                SysCourse.course_name == course_name,
                func.trim(SysCourse.class_name) == class_name,
                SysCourse.course_date == course_date,
            )
            existing_result = await query_db.execute(existing_query)
            existing_course = existing_result.scalar()
            if existing_course and not update_support:
                errors.append(
                    {
                        "rowNum": row_num,
                        "field": "课节/班级/日期",
                        "message": "课程已存在",
                        "value": f"{course_name} - {class_name} - {course_date}",
                    }
                )
                continue

            ok_rows.append(
                {
                    "rowNum": row_num,
                    "existingCourseId": int(existing_course.course_id) if existing_course else None,
                    "course_name": course_name,
                    "subject_name": subject_name,
                    "class_name": class_name,
                    "course_date": course_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "order_num": _infer_order_num(course_name),
                }
            )
        except Exception as e:
            errors.append({"rowNum": row_num, "field": "行处理", "message": str(e), "value": ""})

    return ok_rows, errors


@courseImportController.post("/precheck")
async def precheck_course_excel(
    request: Request,
    file: UploadFile = File(...),
    _update_support: int = Query(default=0, alias="updateSupport"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    try:
        if not file.filename.endswith((".xlsx", ".xls")):
            return ResponseUtil.error(msg="只支持上传.xlsx或.xls格式的Excel文件")

        contents = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            return ResponseUtil.error(msg=f"Excel文件格式错误或已损坏: {str(e)}")

        if df.empty:
            return ResponseUtil.error(msg="Excel文件内容为空，请检查文件")

        required_columns = ["课节", "学科", "班级", "日期"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ResponseUtil.error(msg=f"Excel文件缺少必需的列: {', '.join(missing_columns)}")

        await CourseDao.ensure_schema(query_db)
        system_classes_list = await UserClassService.get_distinct_student_classes(query_db)
        system_classes = {str(c).strip() for c in system_classes_list if c and str(c).strip()}

        update_support = int(_update_support or 0) == 1
        ok_rows, errors = await _precheck_course_dataframe(df, system_classes, query_db, update_support=update_support)
        csv_report = _build_error_report_csv(errors) if errors else ""
        return ResponseUtil.success(
            data={
                "pass": len(errors) == 0,
                "totalRows": int(len(df.index)),
                "validRows": int(len(ok_rows)),
                "errorCount": int(len(errors)),
                "errors": errors,
                "errorReportCsv": csv_report,
            }
        )
    except Exception as e:
        await query_db.rollback()
        logger.error(f"课程导入预校验失败: {str(e)}")
        return ResponseUtil.error(msg=f"预校验失败: {str(e)}")


@courseImportController.post("/upload")
async def upload_course_excel(
    request: Request,
    file: UploadFile = File(...),
    _update_support: int = Query(default=0, alias="updateSupport"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    导入课程Excel文件

    参数:
        file: Excel文件
        update_support: 是否更新已存在的数据（0=否，1=是）

    返回:
        成功/失败统计信息
    """
    try:
        # 验证文件类型
        if not file.filename.endswith((".xlsx", ".xls")):
            return ResponseUtil.error(msg="只支持上传.xlsx或.xls格式的Excel文件")

        # 读取文件内容
        contents = await file.read()

        # 尝试读取Excel文件
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            return ResponseUtil.error(msg=f"Excel文件格式错误或已损坏: {str(e)}")

        # 检查是否为空文件
        if df.empty:
            return ResponseUtil.error(msg="Excel文件内容为空，请检查文件")

        # 验证必需的列
        required_columns = ["课节", "学科", "班级", "日期"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ResponseUtil.error(msg=f"Excel文件缺少必需的列: {', '.join(missing_columns)}")

        # 确保数据库表结构正确
        await CourseDao.ensure_schema(query_db)

        system_classes_list = await UserClassService.get_distinct_student_classes(query_db)
        system_classes = {str(c).strip() for c in system_classes_list if c and str(c).strip()}

        update_support = int(_update_support or 0) == 1

        success_count = 0
        ok_rows, errors = await _precheck_course_dataframe(df, system_classes, query_db, update_support=update_support)
        failure_msg: List[str] = [
            f"第{e.get('rowNum')}行：{(str(e.get('field')) + '：') if e.get('field') else ''}{e.get('message')}"
            for e in errors
        ]
        failure_count = len(errors)

        for row in ok_rows:
            row_num = row.get("rowNum") or ""
            try:
                async with query_db.begin_nested():
                    status = "0"
                    existing_course_id = row.get("existingCourseId")
                    if existing_course_id and update_support:
                        await query_db.execute(
                            update(SysCourse)
                            .where(SysCourse.course_id == int(existing_course_id))
                            .values(
                                subject_name=row.get("subject_name"),
                                class_name=row.get("class_name"),
                                course_date=row.get("course_date"),
                                start_time=row.get("start_time"),
                                end_time=row.get("end_time"),
                                order_num=row.get("order_num") or 0,
                                status=status,
                                update_by=current_user.user.user_name,
                                update_time=datetime.now(),
                            )
                        )
                        success_count += 1
                    else:
                        new_course = {
                            "course_name": row.get("course_name"),
                            "subject_name": row.get("subject_name"),
                            "class_name": row.get("class_name"),
                            "course_date": row.get("course_date"),
                            "start_time": row.get("start_time"),
                            "end_time": row.get("end_time"),
                            "order_num": row.get("order_num") or 0,
                            "status": status,
                            "create_by": current_user.user.user_name,
                            "create_time": datetime.now(),
                        }
                        await CourseDao.add_course(query_db, new_course)
                        success_count += 1
            except SQLAlchemyError as e:
                failure_msg.append(f"第{row_num}行：{str(e)}")
                failure_count += 1
                logger.error(f"导入第{row_num}行数据失败: {str(e)}")
            except Exception as e:
                failure_msg.append(f"第{row_num}行：{str(e)}")
                failure_count += 1
                logger.error(f"导入第{row_num}行数据失败: {str(e)}")

        # 提交事务
        await query_db.commit()

        # 构建返回消息
        msg_parts = [f"成功导入{success_count}条数据"]
        if failure_count > 0:
            msg_parts.append(f"，失败{failure_count}条")
            if failure_msg:
                msg_parts.append("<br/><br/>错误详情：<br/>")
                msg_parts.append("<br/>".join(failure_msg[:20]))  # 最多显示20条错误
                if failure_count > 20:
                    msg_parts.append(f"<br/>...还有{failure_count - 20}条错误未显示")

        msg = "".join(msg_parts)
        logger.info(f"导入课程Excel完成：成功{success_count}条，失败{failure_count}条")

        return ResponseUtil.success(msg=msg)

    except Exception as e:
        await query_db.rollback()
        logger.error(f"导入课程Excel失败: {str(e)}")
        return ResponseUtil.error(msg=f"导入失败: {str(e)}")


@courseImportController.get("/importTemplate")
async def download_import_template(request: Request):
    """
    下载课程导入模板

    返回:
        Excel文件流
    """
    try:
        output = io.BytesIO()

        # 创建模板数据
        template_data = {
            "课节": ["第1节", "第2节", "第3节"],
            "学科": ["数学", "语文", "英语"],
            "班级": ["2024班", "2024班", "2025班"],
            "日期": ["2024-01-08", "2024-01-08", "2024-01-08"],
            "课节开始时间": ["08:00", "08:55", "10:00"],
            "课节结束时间": ["08:45", "09:40", "10:45"],
        }
        df = pd.DataFrame(template_data)

        # 写入Excel
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="课程信息")

            # 获取工作表
            worksheet = writer.sheets["课程信息"]

            # 设置列宽
            worksheet.column_dimensions["A"].width = 12  # 课节
            worksheet.column_dimensions["B"].width = 15  # 学科
            worksheet.column_dimensions["C"].width = 20  # 班级
            worksheet.column_dimensions["D"].width = 15  # 日期
            worksheet.column_dimensions["E"].width = 15  # 课节开始时间
            worksheet.column_dimensions["F"].width = 15  # 课节结束时间

        output.seek(0)
        logger.info("下载课程导入模板成功")

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=course_import_template.xlsx",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as e:
        logger.error(f"下载课程导入模板失败: {str(e)}")
        return ResponseUtil.error(msg=f"下载模板失败: {str(e)}")
