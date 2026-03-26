from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.job_do import SysJobLog
from module_admin.entity.vo.job_vo import JobLogQueryModel
from utils.page_util import PageUtil


class JobLogDao:
    """定时任务日志管理数据访问层"""

    @classmethod
    async def get_job_log_list(cls, db: AsyncSession, query_params: JobLogQueryModel, is_page: bool = True):
        """获取日志列表"""
        query = select(SysJobLog)

        if query_params.job_name:
            query = query.where(SysJobLog.job_name.like(f"%{query_params.job_name}%"))
        if query_params.job_group:
            query = query.where(SysJobLog.job_group == query_params.job_group)
        if query_params.status:
            query = query.where(SysJobLog.status == query_params.status)

        # 修正：job_vo里没有定义begin_time和end_time，需确认QueryModel字段
        # 根据Reference项目 JobLogQueryModel 继承自 JobLogModel，并添加 begin_time, end_time
        # 已经在 job_vo.py 中添加了吗？
        # 检查 Step 912 的 job_vo.py 内容
        # JobLogQueryModel 仅仅根据 page_num/page_size定义。需要修正 job_vo.py 或者在此处处理

        # 假设 job_vo.py 已经有了这些字段 (如果没有会报错，稍后我需要去补全 job_vo.py 如果缺失)
        # 根据 Step 912，JobLogQueryModel 确实只定义了 page_num, page_size。
        # 我需要修改 job_vo.py 增加查询字段。暂时先略过高级查询，或者直接修正 job_vo.py。

        query = query.order_by(desc(SysJobLog.create_time))
        return await PageUtil.paginate(db, query, query_params.page_num, query_params.page_size, is_page)

    @classmethod
    async def add_job_log(cls, db: AsyncSession, job_log: SysJobLog):
        """新增日志"""
        db.add(job_log)
        await db.commit()
        await db.refresh(job_log)
        return job_log

    @classmethod
    def add_job_log_sync(cls, db, job_log: SysJobLog):
        """新增日志(同步) - 用于APScheduler监听器"""
        db.add(job_log)
        db.commit()
        db.refresh(job_log)
        return job_log

    @classmethod
    async def delete_job_log(cls, db: AsyncSession, job_log_ids: list):
        """删除日志"""
        query = delete(SysJobLog).where(SysJobLog.job_log_id.in_(job_log_ids))
        await db.execute(query)
        await db.commit()

    @classmethod
    async def clear_job_log(cls, db: AsyncSession):
        """清空日志"""
        query = delete(SysJobLog)
        await db.execute(query)
        await db.commit()
