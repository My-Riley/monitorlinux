from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from module_admin.service.login_service import LoginService
from utils.log_util import logger
from utils.response_util import ResponseUtil

genController = APIRouter(prefix="/tool/gen", dependencies=[Depends(LoginService.get_current_user)])


@genController.get("/list")
async def get_gen_list(
    request: Request,
    table_name: Optional[str] = Query(default=None, alias="tableName"),
    table_comment: Optional[str] = Query(default=None, alias="tableComment"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
):
    """获取代码生成表列表"""
    logger.info("获取代码生成表列表成功")
    return ResponseUtil.success(dict_content={"rows": [], "total": 0})


@genController.get("/db/list")
async def get_db_list(
    request: Request,
    table_name: Optional[str] = Query(default=None, alias="tableName"),
    table_comment: Optional[str] = Query(default=None, alias="tableComment"),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
):
    """获取数据库表列表"""
    logger.info("获取数据库表列表成功")
    return ResponseUtil.success(dict_content={"rows": [], "total": 0})


@genController.get("/{table_id}")
async def get_gen_detail(
    request: Request,
    table_id: int,
):
    """获取代码生成表详情"""
    logger.info("获取代码生成表详情成功")
    return ResponseUtil.success(data={})


@genController.put("")
async def update_gen(
    request: Request,
    data: dict,
):
    """修改代码生成表"""
    logger.info("修改代码生成表成功")
    return ResponseUtil.success(msg="修改成功")


@genController.post("/importTable")
async def import_table(
    request: Request,
    tables: str = Query(default=""),
):
    """导入表"""
    logger.info("导入表成功")
    return ResponseUtil.success(msg="导入成功")


@genController.get("/preview/{table_id}")
async def preview_gen(
    request: Request,
    table_id: int,
):
    """预览代码"""
    logger.info("预览代码成功")
    return ResponseUtil.success(data={})


@genController.delete("/{table_ids}")
async def delete_gen(
    request: Request,
    table_ids: str,
):
    """删除代码生成表"""
    logger.info("删除代码生成表成功")
    return ResponseUtil.success(msg="删除成功")


@genController.get("/genCode/{table_name}")
async def gen_code(
    request: Request,
    table_name: str,
):
    """生成代码"""
    logger.info("生成代码成功")
    return ResponseUtil.success(msg="生成成功")


@genController.get("/synchDb/{table_name}")
async def synch_db(
    request: Request,
    table_name: str,
):
    """同步数据库"""
    logger.info("同步数据库成功")
    return ResponseUtil.success(msg="同步成功")
