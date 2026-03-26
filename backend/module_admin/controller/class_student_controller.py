from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.class_student_vo import EditStudentModel, StudentQueryModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.class_student_service import StudentService
from module_admin.service.login_service import LoginService
from module_admin.service.user_class_service import UserClassService
from utils.log_util import logger
from utils.response_util import ResponseUtil

studentController = APIRouter(prefix="/system/student", dependencies=[Depends(LoginService.get_current_user)])


@studentController.get("/list")
async def get_student_list(query: StudentQueryModel = Depends(StudentQueryModel), db: AsyncSession = Depends(get_db)):
    """
    学生分页查询
    """
    result = await StudentService.get_student_list(db, query)
    return ResponseUtil.success(model_content=result)


@studentController.get("/classes")
async def get_all_classes(query_db: AsyncSession = Depends(get_db)):
    classes = await UserClassService.get_distinct_student_class_options(query_db)
    return ResponseUtil.success(data=classes)


@studentController.get("/search")
async def search_students(keyword: Optional[str] = Query(None), query_db: AsyncSession = Depends(get_db)):
    if not keyword or len(keyword.strip()) == 0:
        return ResponseUtil.success(data=[])

    data = await StudentService.search_students_by_keyword(query_db, keyword.strip())
    return ResponseUtil.success(data=data)


@studentController.post("")
async def add_student(
    data: EditStudentModel,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    try:
        await StudentService.add_student(db, data, current_user.user.user_name)
        await db.commit()
        return ResponseUtil.success(msg="新增成功")
    except ValueError as e:
        return ResponseUtil.error(msg=str(e))


@studentController.put("")
async def update_student(
    data: EditStudentModel,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    if not hasattr(data, "id") or data.id is None:
        return ResponseUtil.error(msg="缺少学生ID")

    try:
        await StudentService.update_student(db, data.id, data, current_user.user.user_name)
        await db.commit()
        return ResponseUtil.success(msg="修改成功")
    except ValueError as e:
        await db.rollback()
        return ResponseUtil.error(msg=str(e))


@studentController.delete("/{ids}")
async def delete_students(ids: str, db: AsyncSession = Depends(get_db)):
    # 这里的 ids 约定为“学号 student_id”，支持批量：/system/student/2023001,2023002
    student_id_list = [x.strip() for x in ids.split(",") if x.strip()]
    if not student_id_list:
        return ResponseUtil.error(msg="无效学号")

    await StudentService.batch_delete_students(db, student_id_list)
    await db.commit()
    logger.info(f"成功删除 {len(student_id_list)} 个学生")
    return ResponseUtil.success(msg=f"成功删除 {len(student_id_list)} 个学生")
