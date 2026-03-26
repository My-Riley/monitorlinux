from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.menu_do import SysMenu
from module_admin.entity.do.post_do import SysPost
from module_admin.entity.do.role_do import SysRole, SysRoleMenu
from module_admin.entity.do.user_do import SysUser, SysUserPost, SysUserRole


class UserDao:
    """用户数据访问层"""

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: int):
        """根据用户ID获取用户信息"""
        # 获取用户基本信息
        user_query = select(SysUser).where(SysUser.user_id == user_id, SysUser.del_flag == "0")
        user_result = await db.execute(user_query)
        user_basic_info = user_result.scalar()

        if not user_basic_info:
            return {"user_basic_info": None}

        # 获取部门信息
        dept_query = select(SysDept).where(SysDept.dept_id == user_basic_info.dept_id)
        dept_result = await db.execute(dept_query)
        user_dept_info = dept_result.scalar()

        # 获取角色信息
        role_query = (
            select(SysRole)
            .join(SysUserRole, SysRole.role_id == SysUserRole.role_id)
            .where(SysUserRole.user_id == user_id, SysRole.del_flag == "0")
        )
        role_result = await db.execute(role_query)
        user_role_info = role_result.scalars().all()

        # 获取岗位信息
        post_query = (
            select(SysPost)
            .join(SysUserPost, SysPost.post_id == SysUserPost.post_id)
            .where(SysUserPost.user_id == user_id)
        )
        post_result = await db.execute(post_query)
        user_post_info = post_result.scalars().all()

        # 获取菜单权限信息
        role_ids = [role.role_id for role in user_role_info]
        if role_ids:
            menu_query = (
                select(SysMenu)
                .join(SysRoleMenu, SysMenu.menu_id == SysRoleMenu.menu_id)
                .where(SysRoleMenu.role_id.in_(role_ids), SysMenu.status == "0")
                .distinct()
            )
            menu_result = await db.execute(menu_query)
            user_menu_info = menu_result.scalars().all()
        else:
            user_menu_info = []

        return {
            "user_basic_info": user_basic_info,
            "user_dept_info": user_dept_info,
            "user_role_info": user_role_info,
            "user_post_info": user_post_info,
            "user_menu_info": user_menu_info,
        }

    @classmethod
    async def get_user_by_name(cls, db: AsyncSession, user_name: str):
        """根据用户名获取用户信息"""
        query = select(SysUser).where(SysUser.user_name == user_name, SysUser.del_flag == "0")
        result = await db.execute(query)
        return result.scalar()

    @classmethod
    async def get_user_list(cls, db: AsyncSession, query: select):
        """获取用户列表 (Query object passed from Service)"""
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_dept_list_for_tree(cls, db: AsyncSession):
        """获取部门列表用于构建树"""
        query = (
            select(SysDept)
            .where(
                SysDept.del_flag == "0",
                SysDept.status == "0",
            )
            .order_by(SysDept.order_num)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_all_roles(cls, db: AsyncSession):
        """获取所有角色"""
        query = select(SysRole).where(SysRole.del_flag == "0").order_by(SysRole.role_sort)
        result = await db.execute(query)
        return result.scalars().all()


    @classmethod
    async def add_user(cls, db: AsyncSession, user: SysUser):
        """添加用户"""
        db.add(user)
        await db.flush() # Flush to get ID
        return user

    @classmethod
    async def update_user(cls, db: AsyncSession, user_id: int, update_data: dict):
        """更新用户信息"""
        query = update(SysUser).where(SysUser.user_id == user_id).values(**update_data)
        await db.execute(query)
        # Removed commit here to allow transaction control in Service

    @classmethod
    async def delete_user(cls, db: AsyncSession, user_ids: list, update_data: dict):
        """删除用户(软删除)"""
        query = update(SysUser).where(SysUser.user_id.in_(user_ids)).values(**update_data)
        await db.execute(query)

    @classmethod
    async def delete_user_role_by_user_id(cls, db: AsyncSession, user_id: int):
        """根据用户ID删除用户角色关联"""
        query = delete(SysUserRole).where(SysUserRole.user_id == user_id)
        await db.execute(query)

    @classmethod
    async def add_user_role(cls, db: AsyncSession, user_role: SysUserRole):
        """添加用户角色关联"""
        db.add(user_role)

    @classmethod
    async def delete_user_post_by_user_id(cls, db: AsyncSession, user_id: int):
        """根据用户ID删除用户岗位关联"""
        query = delete(SysUserPost).where(SysUserPost.user_id == user_id)
        await db.execute(query)

    @classmethod
    async def add_user_post(cls, db: AsyncSession, user_post: SysUserPost):
        """添加用户岗位关联"""
        db.add(user_post)

    @classmethod
    async def get_user_role_ids(cls, db: AsyncSession, user_id: int):
        """获取用户角色ID列表"""
        query = select(SysUserRole.role_id).where(SysUserRole.user_id == user_id)
        result = await db.execute(query)
        return [int(row[0]) for row in result.fetchall()]

    @classmethod
    async def get_user_post_ids(cls, db: AsyncSession, user_id: int):
        """获取用户岗位ID列表"""
        query = select(SysUserPost.post_id).where(SysUserPost.user_id == user_id)
        result = await db.execute(query)
        return [int(row[0]) for row in result.fetchall()]

    @classmethod
    async def check_user_allowed(cls, db: AsyncSession, user_id: int):
        """校验用户是否允许操作"""
        # Check if super admin
        if user_id == 1:
            return False
        return True
