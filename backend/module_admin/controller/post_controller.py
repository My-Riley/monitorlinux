import io
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.entity.do.post_do import SysPost
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import CamelCaseUtil
from utils.log_util import logger
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil

postController = APIRouter(prefix="/system/post", dependencies=[Depends(LoginService.get_current_user)])


class PostEditModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)
    post_id: Optional[int] = Field(default=None)
    post_code: Optional[str] = Field(default=None)
    post_name: Optional[str] = Field(default=None)
    post_sort: Optional[int] = Field(default=None)
    status: Optional[str] = Field(default=None)
    remark: Optional[str] = Field(default=None)


@postController.get("/list")
async def get_post_list(
    request: Request,
    post_code: Optional[str] = Query(default=None, alias="postCode"),
    post_name: Optional[str] = Query(default=None, alias="postName"),
    status: Optional[str] = Query(default=None),
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=10, alias="pageSize"),
    query_db: AsyncSession = Depends(get_db),
):
    """获取岗位列表"""
    query = select(SysPost)
    if post_code:
        query = query.where(SysPost.post_code.like(f"%{post_code}%"))
    if post_name:
        query = query.where(SysPost.post_name.like(f"%{post_name}%"))
    if status:
        query = query.where(SysPost.status == status)
    query = query.order_by(SysPost.post_sort)
    result = await PageUtil.paginate(query_db, query, page_num, page_size, True)
    logger.info("获取岗位列表成功")
    return ResponseUtil.success(model_content=result)


@postController.get("/{post_id}")
async def get_post_detail(
    request: Request,
    post_id: int,
    query_db: AsyncSession = Depends(get_db),
):
    """获取岗位详情"""
    query = select(SysPost).where(SysPost.post_id == post_id)
    result = await query_db.execute(query)
    post = result.scalar()
    logger.info("获取岗位详情成功")
    return ResponseUtil.success(data=CamelCaseUtil.transform_result(post))


@postController.post("")
@Log(title="岗位管理", business_type=1)
async def add_post(
    request: Request,
    post_data: PostEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增岗位"""
    post = SysPost(
        post_code=post_data.post_code,
        post_name=post_data.post_name,
        post_sort=post_data.post_sort or 0,
        status=post_data.status or "0",
        create_by=current_user.user.user_name,
        create_time=datetime.now(),
        remark=post_data.remark,
    )
    query_db.add(post)
    await query_db.commit()
    logger.info("新增岗位成功")
    return ResponseUtil.success(msg="新增成功")


@postController.put("")
@Log(title="岗位管理", business_type=2)
async def update_post(
    request: Request,
    post_data: PostEditModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改岗位"""
    update_data = {
        "post_code": post_data.post_code,
        "post_name": post_data.post_name,
        "post_sort": post_data.post_sort,
        "status": post_data.status,
        "update_by": current_user.user.user_name,
        "update_time": datetime.now(),
        "remark": post_data.remark,
    }
    query = update(SysPost).where(SysPost.post_id == post_data.post_id).values(**update_data)
    await query_db.execute(query)
    await query_db.commit()
    logger.info("修改岗位成功")
    return ResponseUtil.success(msg="修改成功")


@postController.delete("/{post_ids}")
@Log(title="岗位管理", business_type=3)
async def delete_post(
    request: Request,
    post_ids: str,
    query_db: AsyncSession = Depends(get_db),
):
    """删除岗位"""
    from sqlalchemy import delete as sql_delete

    ids = post_ids.split(",")
    for pid in ids:
        query = sql_delete(SysPost).where(SysPost.post_id == int(pid))
        await query_db.execute(query)
    await query_db.commit()
    logger.info("删除岗位成功")
    return ResponseUtil.success(msg="删除成功")


@postController.post("/export")
@Log(title="岗位管理", business_type=5)
async def export_post(
    request: Request,
    post_code: Optional[str] = Form(default=None, alias="postCode"),
    post_name: Optional[str] = Form(default=None, alias="postName"),
    status: Optional[str] = Form(default=None),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导出岗位列表"""
    query = select(SysPost)
    if post_code:
        query = query.where(SysPost.post_code.like(f"%{post_code}%"))
    if post_name:
        query = query.where(SysPost.post_name.like(f"%{post_name}%"))
    if status:
        query = query.where(SysPost.status == status)

    query = query.order_by(SysPost.post_sort)
    result = await query_db.execute(query)
    posts = result.scalars().all()

    data = []
    for post in posts:
        data.append(
            {
                "岗位编号": post.post_id,
                "岗位编码": post.post_code,
                "岗位名称": post.post_name,
                "显示顺序": post.post_sort,
                "状态": "正常" if post.status == "0" else "停用",
                "创建时间": post.create_time.strftime("%Y-%m-%d %H:%M:%S") if post.create_time else "",
            }
        )

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="岗位数据")

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=post_list.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
