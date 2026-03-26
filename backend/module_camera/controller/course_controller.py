from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.service.user_class_service import UserClassService
from module_camera.dao.course_dao import CourseDao
from module_camera.service.course_service import CourseService
from utils.response_util import ResponseUtil

router = APIRouter(prefix="/cell/course", tags=["课程管理"])


@router.get("/classes")
async def get_course_classes(db: AsyncSession = Depends(get_db)):
    """获取班级下拉选项"""
    classes = await UserClassService.get_distinct_student_class_options(db)
    return ResponseUtil.success(data=classes)


@router.get("/subjects")
async def get_course_subjects(db: AsyncSession = Depends(get_db)):
    """获取学科下拉选项"""
    subjects = await CourseService.get_distinct_subject_names(db)
    return ResponseUtil.success(data=subjects)


@router.get("/weeks")
async def get_course_weeks(
    semester_id: str = Query(None, alias="semesterId"),
    db: AsyncSession = Depends(get_db),
):
    week_nums = await CourseDao.list_course_week_nums(db, semester_id)
    return ResponseUtil.success(data=week_nums)


@router.get("/list")
async def get_course_list(
    request: Request,
    course_name: str = Query(None, alias="courseName", description="课程名称"),
    subject_name: str = Query(None, alias="subjectName", description="学科"),
    class_name: str = Query(None, alias="className", description="班级"),
    status: str = Query(None, description="状态"),
    course_date: str = Query(None, alias="courseDate", description="日期"),
    semester_id: str = Query(None, alias="semesterId", description="学期"),
    week_num: int = Query(None, alias="weekNum", description="周次"),
    page_num: int = Query(1, alias="pageNum", description="页码"),
    page_size: int = Query(10, alias="pageSize", description="每页大小"),
    db: AsyncSession = Depends(get_db),
):
    """获取课程列表"""
    has_paging = "pageNum" in request.query_params or "pageSize" in request.query_params
    query_params = {
        "course_name": course_name,
        "subject_name": subject_name,
        "class_name": class_name,
        "status": status,
        "course_date": course_date,
        "semester_id": semester_id,
        "week_num": week_num,
        "page_num": page_num,
        "page_size": page_size,
    }

    if has_paging:
        result, total = await CourseService.get_course_list(db, query_params, is_page=True)
        return ResponseUtil.success(rows=result, dict_content={"total": total})
    else:
        result = await CourseService.get_course_list(db, query_params, is_page=False)
        return ResponseUtil.success(data=result)


@router.get("/{course_id}")
async def get_course(course_id: int, db: AsyncSession = Depends(get_db)):
    """获取课程详情"""
    result = await CourseService.get_course_by_id(db, course_id)
    if result:
        return ResponseUtil.success(data=result)
    return ResponseUtil.failure(msg="课程不存在")


@router.post("")
async def add_course(request: Request, db: AsyncSession = Depends(get_db)):
    """新增课程"""
    data = await request.json()
    try:
        await CourseService.add_course(db, data)
        return ResponseUtil.success(msg="新增成功")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))


@router.put("")
async def update_course(request: Request, db: AsyncSession = Depends(get_db)):
    """修改课程"""
    data = await request.json()
    try:
        await CourseService.update_course(db, data)
        return ResponseUtil.success(msg="修改成功")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))


@router.delete("/{course_ids}")
async def delete_course(course_ids: str, db: AsyncSession = Depends(get_db)):
    """删除课程"""
    await CourseService.delete_course(db, course_ids)
    return ResponseUtil.success(msg="删除成功")
