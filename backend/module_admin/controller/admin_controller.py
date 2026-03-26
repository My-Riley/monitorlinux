from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.post_do import SysPost
from module_admin.entity.do.role_do import SysRole
from module_admin.entity.do.user_do import SysUser, SysUserPost, SysUserRole
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import PwdUtil
from utils.log_util import logger
from utils.page_util import PageUtil
from utils.response_util import ResponseUtil

adminController = APIRouter(
    prefix="/system/admin", dependencies=[Depends(LoginService.get_current_user)], tags=["管理员用户管理"]
)


@adminController.get("/list")
async def get_admin_list(
    request: Request,
    pageNum: int = Query(1, alias="pageNum"),
    pageSize: int = Query(10, alias="pageSize"),
    userName: Optional[str] = Query(None, alias="userName"),
    phonenumber: Optional[str] = Query(None, alias="phonenumber"),
    status: Optional[str] = Query(None, alias="status"),
    deptId: Optional[int] = Query(None, alias="deptId"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取管理员用户列表"""
    try:
        # 构建查询条件
        query = select(SysUser).where(
            SysUser.del_flag == "0",
            SysUser.user_type != "00",  # 排除学生用户
        )

        # 添加筛选条件
        if userName:
            query = query.where(SysUser.user_name.like(f"%{userName}%"))
        if phonenumber:
            query = query.where(SysUser.phonenumber.like(f"%{phonenumber}%"))
        if status:
            query = query.where(SysUser.status == status)
        if deptId:
            query = query.where(SysUser.dept_id == deptId)

        # 排序
        query = query.order_by(SysUser.create_time.desc())

        # 分页查询
        result = await PageUtil.paginate(query_db, query, pageNum, pageSize, is_page=True)

        # 查询部门信息
        for user in result.rows:
            if hasattr(user, "dept_id") and user.dept_id:
                dept_query = select(SysDept).where(SysDept.dept_id == user.dept_id)
                dept_result = await query_db.execute(dept_query)
                dept = dept_result.scalar()
                if dept:
                    user.dept = {"deptName": dept.dept_name}

        return ResponseUtil.success(model_content=result)

    except Exception as e:
        logger.error(f"获取管理员用户列表失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取管理员用户列表失败: {str(e)}")


@adminController.get("/{user_id}")
async def get_admin_info(
    user_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取管理员用户详细信息"""
    try:
        # 查询用户信息
        user_query = select(SysUser).where(SysUser.user_id == user_id, SysUser.del_flag == "0")
        user_result = await query_db.execute(user_query)
        user = user_result.scalar()

        if not user:
            return ResponseUtil.error(msg="用户不存在")

        # 查询用户角色
        role_query = select(SysUserRole.role_id).where(SysUserRole.user_id == user_id)
        role_result = await query_db.execute(role_query)
        role_ids = [row[0] for row in role_result.fetchall()]

        # 查询用户岗位
        post_query = select(SysUserPost.post_id).where(SysUserPost.user_id == user_id)
        post_result = await query_db.execute(post_query)
        post_ids = [row[0] for row in post_result.fetchall()]

        # 查询所有角色
        roles_query = select(SysRole).where(SysRole.del_flag == "0")
        roles_result = await query_db.execute(roles_query)
        roles = roles_result.scalars().all()

        # 查询所有岗位
        posts_query = select(SysPost).where(SysPost.status == "0")
        posts_result = await query_db.execute(posts_query)
        posts = posts_result.scalars().all()

        return ResponseUtil.success(
            data={"data": user, "roleIds": role_ids, "postIds": post_ids, "roles": roles, "posts": posts}
        )

    except Exception as e:
        logger.error(f"获取管理员用户信息失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取管理员用户信息失败: {str(e)}")


@adminController.get("")
async def get_admin_create_info(
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取新增管理员用户所需信息"""
    try:
        # 查询所有角色
        roles_query = select(SysRole).where(SysRole.del_flag == "0", SysRole.role_id != 1)
        roles_result = await query_db.execute(roles_query)
        roles = roles_result.scalars().all()

        # 查询所有岗位
        posts_query = select(SysPost).where(SysPost.status == "0")
        posts_result = await query_db.execute(posts_query)
        posts = posts_result.scalars().all()

        return ResponseUtil.success(data={"roles": roles, "posts": posts})

    except Exception as e:
        logger.error(f"获取新增信息失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取新增信息失败: {str(e)}")


@adminController.post("")
async def add_admin(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增管理员用户"""
    try:
        data = await request.json()

        # 检查用户名是否已存在
        check_query = select(SysUser).where(SysUser.user_name == data.get("userName"), SysUser.del_flag == "0")
        check_result = await query_db.execute(check_query)
        if check_result.scalar():
            return ResponseUtil.error(msg="用户名已存在")

        # 密码加密
        hashed_password = PwdUtil.get_password_hash(data.get("password", "123456"))

        # 创建用户
        new_user = SysUser(
            user_name=data.get("userName"),
            nick_name=data.get("nickName"),
            user_type="01",  # 管理员类型
            email=data.get("email"),
            phonenumber=data.get("phonenumber"),
            sex=data.get("sex", "0"),
            password=hashed_password,
            dept_id=data.get("deptId"),
            status=data.get("status", "0"),
            remark=data.get("remark"),
            create_by=current_user.user.user_name,
            create_time=datetime.now(),
            del_flag="0",
        )
        query_db.add(new_user)
        await query_db.flush()

        # 添加用户角色关联
        role_ids = data.get("roleIds", [])
        for role_id in role_ids:
            user_role = SysUserRole(user_id=new_user.user_id, role_id=role_id)
            query_db.add(user_role)

        # 添加用户岗位关联
        post_ids = data.get("postIds", [])
        for post_id in post_ids:
            user_post = SysUserPost(user_id=new_user.user_id, post_id=post_id)
            query_db.add(user_post)

        await query_db.commit()

        logger.info(f"新增管理员用户成功: {data.get('userName')}")
        return ResponseUtil.success(msg="新增成功")

    except Exception as e:
        await query_db.rollback()
        logger.error(f"新增管理员用户失败: {str(e)}")
        return ResponseUtil.error(msg=f"新增失败: {str(e)}")


@adminController.put("")
async def update_admin(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改管理员用户"""
    try:
        data = await request.json()
        user_id = data.get("userId")

        if not user_id:
            return ResponseUtil.error(msg="用户ID不能为空")

        # 更新用户信息
        update_data = {
            "nick_name": data.get("nickName"),
            "email": data.get("email"),
            "phonenumber": data.get("phonenumber"),
            "sex": data.get("sex"),
            "dept_id": data.get("deptId"),
            "status": data.get("status"),
            "remark": data.get("remark"),
            "update_by": current_user.user.user_name,
            "update_time": datetime.now(),
        }

        update_stmt = update(SysUser).where(SysUser.user_id == user_id).values(**update_data)
        await query_db.execute(update_stmt)

        # 删除原有角色关联
        delete_role_stmt = delete(SysUserRole).where(SysUserRole.user_id == user_id)
        await query_db.execute(delete_role_stmt)

        # 添加新的角色关联
        role_ids = data.get("roleIds", [])
        for role_id in role_ids:
            user_role = SysUserRole(user_id=user_id, role_id=role_id)
            query_db.add(user_role)

        # 删除原有岗位关联
        delete_post_stmt = delete(SysUserPost).where(SysUserPost.user_id == user_id)
        await query_db.execute(delete_post_stmt)

        # 添加新的岗位关联
        post_ids = data.get("postIds", [])
        for post_id in post_ids:
            user_post = SysUserPost(user_id=user_id, post_id=post_id)
            query_db.add(user_post)

        await query_db.commit()

        logger.info(f"修改管理员用户成功: {user_id}")
        return ResponseUtil.success(msg="修改成功")

    except Exception as e:
        await query_db.rollback()
        logger.error(f"修改管理员用户失败: {str(e)}")
        return ResponseUtil.error(msg=f"修改失败: {str(e)}")


@adminController.delete("/{user_ids}")
async def delete_admin(
    user_ids: str,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """删除管理员用户（硬删除）"""
    try:
        ids = [int(id) for id in user_ids.split(",")]

        # 不能删除超级管理员
        if 1 in ids:
            return ResponseUtil.error(msg="不能删除超级管理员")

        # 先删除用户角色关联
        delete_role_stmt = delete(SysUserRole).where(SysUserRole.user_id.in_(ids))
        await query_db.execute(delete_role_stmt)

        # 删除用户岗位关联
        delete_post_stmt = delete(SysUserPost).where(SysUserPost.user_id.in_(ids))
        await query_db.execute(delete_post_stmt)

        # 硬删除用户
        delete_user_stmt = delete(SysUser).where(SysUser.user_id.in_(ids))
        await query_db.execute(delete_user_stmt)

        await query_db.commit()

        logger.info(f"删除管理员用户成功: {user_ids}")
        return ResponseUtil.success(msg="删除成功")

    except Exception as e:
        await query_db.rollback()
        logger.error(f"删除管理员用户失败: {str(e)}")
        return ResponseUtil.error(msg=f"删除失败: {str(e)}")


@adminController.put("/resetPwd")
async def reset_admin_pwd(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """重置管理员用户密码"""
    try:
        data = await request.json()
        user_id = data.get("userId")
        password = data.get("password")

        if not user_id or not password:
            return ResponseUtil.error(msg="参数错误")

        # 密码加密
        hashed_password = PwdUtil.get_password_hash(password)

        # 更新密码
        update_stmt = (
            update(SysUser)
            .where(SysUser.user_id == user_id)
            .values(password=hashed_password, update_by=current_user.user.user_name, update_time=datetime.now())
        )
        await query_db.execute(update_stmt)
        await query_db.commit()

        logger.info(f"重置管理员密码成功: {user_id}")
        return ResponseUtil.success(msg="密码重置成功")

    except Exception as e:
        await query_db.rollback()
        logger.error(f"重置管理员密码失败: {str(e)}")
        return ResponseUtil.error(msg=f"密码重置失败: {str(e)}")


@adminController.put("/changeStatus")
async def change_admin_status(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """修改管理员用户状态"""
    try:
        data = await request.json()
        user_id = data.get("userId")
        status = data.get("status")

        if not user_id or status is None:
            return ResponseUtil.error(msg="参数错误")

        # 不能停用超级管理员
        if user_id == 1 and status == "1":
            return ResponseUtil.error(msg="不能停用超级管理员")

        # 更新状态
        update_stmt = (
            update(SysUser)
            .where(SysUser.user_id == user_id)
            .values(status=status, update_by=current_user.user.user_name, update_time=datetime.now())
        )
        await query_db.execute(update_stmt)
        await query_db.commit()

        logger.info(f"修改管理员状态成功: {user_id} -> {status}")
        return ResponseUtil.success(msg="状态修改成功")

    except Exception as e:
        await query_db.rollback()
        logger.error(f"修改管理员状态失败: {str(e)}")
        return ResponseUtil.error(msg=f"状态修改失败: {str(e)}")
