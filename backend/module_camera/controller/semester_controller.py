from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_camera.service.semester_service import SemesterService
from utils.response_util import ResponseUtil

router = APIRouter(prefix="/cell/semester", tags=["学期管理"])


@router.get("/list")
async def get_semesters(query_db: AsyncSession = Depends(get_db)):
    """获取所有学期列表"""
    semesters = await SemesterService.get_all_semesters(query_db)
    current = await SemesterService.get_current_semester(query_db)
    return ResponseUtil.success(data={"semesters": semesters, "currentSemesterId": current["id"] if current else None})


@router.post("")
async def add_semester(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    try:
        await SemesterService.create_semester(db, data)
        return ResponseUtil.success(msg="新增成功")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))


@router.put("")
async def update_semester(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    try:
        await SemesterService.update_semester(db, data)
        return ResponseUtil.success(msg="修改成功")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))


@router.delete("/{ids}")
async def delete_semester(ids: str, db: AsyncSession = Depends(get_db)):
    await SemesterService.delete_semester(db, ids)
    return ResponseUtil.success(msg="删除成功")


# Cycle endpoints
@router.get("/cycles")
async def list_cycles(semesterId: str, db: AsyncSession = Depends(get_db)):
    result = await SemesterService.get_cycles(db, semesterId)
    return ResponseUtil.success(data=result)


@router.post("/cycle")
async def add_cycle(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    try:
        await SemesterService.create_cycle(db, data)
        return ResponseUtil.success(msg="新增成功")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))


@router.put("/cycle")
async def update_cycle(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    try:
        await SemesterService.update_cycle(db, data)
        return ResponseUtil.success(msg="修改成功")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))


@router.delete("/cycle/{id}")
async def delete_cycle(id: int, db: AsyncSession = Depends(get_db)):
    await SemesterService.delete_cycle(db, id)
    return ResponseUtil.success(msg="删除成功")


@router.get("/weeks")
async def get_semester_weeks(semesterId: str, db: AsyncSession = Depends(get_db)):
    result = await SemesterService.get_semester_weeks(db, semesterId)
    return ResponseUtil.success(data=result)
