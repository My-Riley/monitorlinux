from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.dao.notice_dao import NoticeDao
from module_admin.entity.do.notice_do import SysNotice
from module_admin.entity.vo.notice_vo import NoticeModel, NoticeQueryModel


class NoticeService:
    """通知公告服务层"""

    @classmethod
    async def get_notice_list_services(cls, db: AsyncSession, query_params: NoticeQueryModel, is_page: bool = True):
        """获取列表"""
        return await NoticeDao.get_notice_list(db, query_params, is_page)

    @classmethod
    async def add_notice_services(cls, db: AsyncSession, notice_data: NoticeModel):
        """新增通知"""
        notice = SysNotice(**notice_data.model_dump(exclude_unset=True))
        return await NoticeDao.add_notice(db, notice)

    @classmethod
    async def edit_notice_services(cls, db: AsyncSession, notice_data: NoticeModel):
        """更新通知"""
        update_data = notice_data.model_dump(exclude_unset=True)
        notice_id = update_data.pop("notice_id")
        await NoticeDao.update_notice(db, notice_id, update_data)
        return True

    @classmethod
    async def delete_notice_services(cls, db: AsyncSession, notice_ids: str):
        """批量删除"""
        ids = [int(i) for i in notice_ids.split(",")]
        await NoticeDao.delete_notice(db, ids)
        return True

    @classmethod
    async def notice_detail_services(cls, db: AsyncSession, notice_id: int):
        """获取详情"""
        notice = await NoticeDao.get_notice_detail_by_id(db, notice_id)
        if notice:
            return NoticeModel.model_validate(notice)
        return None
