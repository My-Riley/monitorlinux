from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.job_do import SysJob
from module_admin.entity.vo.job_vo import JobQueryModel
from utils.page_util import PageUtil


class JobDao:
    """定时任务管理数据访问层"""

    @classmethod
    async def get_job_detail_by_id(cls, db: AsyncSession, job_id: int):
        """获取详情"""
        result = await db.execute(select(SysJob).where(SysJob.job_id == job_id))
        return result.scalars().first()

    @classmethod
    async def get_job_list(cls, db: AsyncSession, query_params: JobQueryModel, is_page: bool = True):
        """获取任务列表"""
        query = select(SysJob)
        if query_params.job_name:
            query = query.where(SysJob.job_name.like(f"%{query_params.job_name}%"))
        if query_params.job_group:
            query = query.where(SysJob.job_group == query_params.job_group)
        if query_params.status:
            query = query.where(SysJob.status == query_params.status)

        query = query.order_by(SysJob.job_id)
        return await PageUtil.paginate(db, query, query_params.page_num, query_params.page_size, is_page)

    @classmethod
    async def get_job_list_for_scheduler(cls, db: AsyncSession):
        """获取所有正常的定时任务"""
        result = await db.execute(select(SysJob).where(SysJob.status == "0"))
        return result.scalars().all()

    @classmethod
    async def get_job_by_name_and_group(cls, db: AsyncSession, job_name: str, job_group: str):
        """根据任务名称和组名查询"""
        query = select(SysJob).where(SysJob.job_name == job_name, SysJob.job_group == job_group)
        result = await db.execute(query)
        return result.scalars().first()

    @classmethod
    async def add_job(cls, db: AsyncSession, job: SysJob):
        """新增任务"""
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return job

    @classmethod
    async def update_job(cls, db: AsyncSession, job_id: int, update_data: dict):
        """更新任务"""
        query = update(SysJob).where(SysJob.job_id == job_id).values(**update_data)
        await db.execute(query)
        await db.commit()

    @classmethod
    async def delete_job(cls, db: AsyncSession, job_ids: list):
        """删除任务"""
        query = delete(SysJob).where(SysJob.job_id.in_(job_ids))
        await db.execute(query)
        await db.commit()
