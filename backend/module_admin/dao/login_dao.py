from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.user_do import SysUser


async def login_by_account(db: AsyncSession, user_name: str):
    """根据用户名查询用户信息"""
    query = (
        select(SysUser, SysDept)
        .outerjoin(SysDept, SysUser.dept_id == SysDept.dept_id)
        .where(SysUser.user_name == user_name, SysUser.del_flag == "0")
    )
    result = await db.execute(query)
    user_info = result.first()
    return user_info
