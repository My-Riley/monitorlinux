from datetime import datetime, time

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.notice_do import SysNotice
from module_admin.entity.vo.notice_vo import NoticeQueryModel
from utils.page_util import PageUtil


class NoticeDao:
    """通知公告数据访问层"""

    @classmethod
    async def get_notice_detail_by_id(cls, db: AsyncSession, notice_id: int):
        """根据ID获取详情"""
        result = await db.execute(select(SysNotice).where(SysNotice.notice_id == notice_id))
        return result.scalars().first()

    @classmethod
    async def get_notice_list(cls, db: AsyncSession, query_params: NoticeQueryModel, is_page: bool = True):
        """获取通知公告列表"""
        query = select(SysNotice)
        if query_params.notice_title:
            query = query.where(SysNotice.notice_title.like(f"%{query_params.notice_title}%"))
        if query_params.notice_type:
            query = query.where(SysNotice.notice_type == query_params.notice_type)
        if query_params.create_by:
            query = query.where(SysNotice.create_by.like(f"%{query_params.create_by}%"))
        if query_params.status:
            query = query.where(SysNotice.status == query_params.status)

        if query_params.begin_time and query_params.end_time:
            begin = datetime.combine(datetime.strptime(query_params.begin_time, "%Y-%m-%d"), time(0, 0, 0))
            end = datetime.combine(datetime.strptime(query_params.end_time, "%Y-%m-%d"), time(23, 59, 59))
            query = query.where(SysNotice.create_time.between(begin, end))

        query = query.order_by(SysNotice.create_time.desc())

        return await PageUtil.paginate(db, query, query_params.page_num, query_params.page_size, is_page)

    @classmethod
    async def add_notice(cls, db: AsyncSession, notice: SysNotice):
        """新增通知公告"""
        db.add(notice)
        await db.commit()
        await db.refresh(notice)
        return notice

    @classmethod
    async def update_notice(cls, db: AsyncSession, notice_id: int, update_data: dict):
        """更新通知公告"""
        query = update(SysNotice).where(SysNotice.notice_id == notice_id).values(**update_data)
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete_notice(cls, db: AsyncSession, notice_ids: list):
        """批量删除通知公告"""
        query = delete(SysNotice).where(SysNotice.notice_id.in_(notice_ids))
        await db.execute(query)
        await db.commit()
