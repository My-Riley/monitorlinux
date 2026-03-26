import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from fastapi import UploadFile
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exception import ServiceException
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.post_do import SysPost
from module_admin.entity.do.role_do import SysRole
from module_admin.entity.do.user_do import SysUser, SysUserPost, SysUserRole
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.entity.vo.user_vo import EditUserModel, UserModel
from utils.common_util import CamelCaseUtil, PwdUtil
from utils.log_util import logger
from utils.page_util import PageUtil


class UserService:
    """用户管理服务层"""

    @classmethod
    async def get_user_list_services(
        cls,
        query_db: AsyncSession,
        page_object: UserModel,
        page_num: int,
        page_size: int,
        begin_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ):
        """获取用户列表"""
        query = select(SysUser).where(SysUser.del_flag == "0")
        if page_object.user_name:
            query = query.where(SysUser.user_name == page_object.user_name)
        if page_object.nick_name:
            query = query.where(
                or_(
                    SysUser.nick_name.like(f"%{page_object.nick_name}%"),
                    SysUser.user_name.like(f"%{page_object.nick_name}%"),
                )
            )
        if page_object.phonenumber:
            query = query.where(SysUser.phonenumber.like(f"%{page_object.phonenumber}%"))
        if page_object.status:
            query = query.where(SysUser.status == page_object.status)
        if page_object.dept_id:
            query = query.where(SysUser.dept_id == page_object.dept_id)

        if begin_time:
            query = query.where(SysUser.create_time >= begin_time)
        if end_time:
            query = query.where(SysUser.create_time <= end_time)

        query = query.order_by(SysUser.create_time.desc())
        return await PageUtil.paginate(query_db, query, page_num, page_size, True)

    @classmethod
    async def add_user_services(
        cls, query_db: AsyncSession, user_model: EditUserModel, current_user_name: str, current_user_id: int
    ):
        """新增用户"""
        existing = await UserDao.get_user_by_name(query_db, user_model.user_name)
        if existing:
            raise ServiceException(message="用户名已存在")

        if user_model.role_ids and 1 in user_model.role_ids:
            raise ServiceException(message="禁止赋予超级管理员角色")

        password = user_model.password or "123456"
        if len(password) > 72:
            password = password[:72]
        password_hash = PwdUtil.get_password_hash(password)

        user = SysUser(
            dept_id=user_model.dept_id,
            user_name=user_model.user_name,
            nick_name=user_model.nick_name or user_model.user_name,
            email=user_model.email,
            phonenumber=user_model.phonenumber,
            sex=user_model.sex,
            password=password_hash,
            status=user_model.status or "0",
            create_by=current_user_name,
            create_time=datetime.now(),
            remark=user_model.remark,
            user_type=user_model.type or "00",
        )

        try:
            added_user = await UserDao.add_user(query_db, user)

            if user_model.role_ids:
                for role_id in set(user_model.role_ids):
                    user_role = SysUserRole(user_id=added_user.user_id, role_id=role_id)
                    await UserDao.add_user_role(query_db, user_role)

            if user_model.post_ids:
                for post_id in set(user_model.post_ids):
                    user_post = SysUserPost(user_id=added_user.user_id, post_id=post_id)
                    await UserDao.add_user_post(query_db, user_post)

            await query_db.commit()
            return CrudResponseModel(is_success=True, message="新增成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def update_user_services(
        cls, query_db: AsyncSession, user_model: EditUserModel, current_user_name: str, current_user_id: int
    ):
        """修改用户"""
        if not await UserDao.check_user_allowed(query_db, user_model.user_id):
            raise ServiceException(message="不允许操作超级管理员用户")

        if user_model.role_ids and 1 in user_model.role_ids:
            # If target user is not user_id=1, they cannot have role_id=1
            if user_model.user_id != 1:
                raise ServiceException(message="禁止赋予超级管理员角色")

        update_data = {
            "dept_id": user_model.dept_id,
            "nick_name": user_model.nick_name,
            "email": user_model.email,
            "phonenumber": user_model.phonenumber,
            "sex": user_model.sex,
            "status": user_model.status,
            "update_by": current_user_name,
            "update_time": datetime.now(),
            "remark": user_model.remark,
            "user_type": user_model.type,
        }
        # Filter None
        update_data = {k: v for k, v in update_data.items() if v is not None}

        try:
            await UserDao.update_user(query_db, user_model.user_id, update_data)

            # Check if role_ids is passed (not None). If it is [], it means clear all.
            if user_model.role_ids is not None:
                await UserDao.delete_user_role_by_user_id(query_db, user_model.user_id)
                for role_id in set(user_model.role_ids):
                    user_role = SysUserRole(user_id=user_model.user_id, role_id=role_id)
                    await UserDao.add_user_role(query_db, user_role)

            if user_model.post_ids is not None:
                await UserDao.delete_user_post_by_user_id(query_db, user_model.user_id)
                for post_id in set(user_model.post_ids):
                    user_post = SysUserPost(user_id=user_model.user_id, post_id=post_id)
                    await UserDao.add_user_post(query_db, user_post)

            await query_db.commit()
            return CrudResponseModel(is_success=True, message="修改成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def delete_user_services(
        cls, query_db: AsyncSession, user_ids: str, current_user_id: int, current_user_name: str
    ):
        """删除用户"""
        try:
            ids = [int(id) for id in user_ids.split(",")]
        except ValueError:
            raise ServiceException(message="参数错误")

        if 1 in ids:
            raise ServiceException(message="不允许删除超级管理员")
        if current_user_id in ids:
            raise ServiceException(message="当前登录用户不能删除")

        update_data = {"del_flag": "2", "update_by": current_user_name, "update_time": datetime.now()}

        try:
            await UserDao.delete_user(query_db, ids, update_data)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message="删除成功")
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def get_user_for_add_services(cls, query_db: AsyncSession):
        """新增用户时获取角色和岗位列表"""
        roles_query = select(SysRole).where(SysRole.del_flag == "0", SysRole.role_id != 1)
        roles_result = await query_db.execute(roles_query)
        roles = roles_result.scalars().all()

        posts_query = select(SysPost)
        posts_result = await query_db.execute(posts_query)
        posts = posts_result.scalars().all()

        return {"roles": CamelCaseUtil.transform_result(roles), "posts": CamelCaseUtil.transform_result(posts)}

    @classmethod
    async def get_user_detail_for_edit_services(cls, query_db: AsyncSession, user_id: int, current_user_id: int):
        """获取用户详细信息(用于编辑)"""
        user_query = select(SysUser).where(SysUser.user_id == user_id, SysUser.del_flag == "0")
        user_result = await query_db.execute(user_query)
        user = user_result.scalar()

        if not user:
            raise ServiceException(message="用户不存在")

        role_ids = await UserDao.get_user_role_ids(query_db, user_id)
        post_ids = await UserDao.get_user_post_ids(query_db, user_id)

        roles_query = select(SysRole).where(SysRole.del_flag == "0")
        roles_result = await query_db.execute(roles_query)
        roles = roles_result.scalars().all()

        posts_query = select(SysPost).where(SysPost.status == "0")
        posts_result = await query_db.execute(posts_query)
        posts = posts_result.scalars().all()

        user_data = CamelCaseUtil.transform_result(user)
        user_data["roleIds"] = role_ids
        user_data["postIds"] = post_ids

        # 如果用户不是超级管理员，则不返回超级管理员角色选项，保证超级管理员唯一性
        if user_id != 1:
            roles = [role for role in roles if role.role_id != 1]
            # 过滤掉已有的超级管理员角色ID，防止数据不一致导致无法编辑
            if 1 in role_ids:
                role_ids = [rid for rid in role_ids if rid != 1]
                user_data["roleIds"] = role_ids

        return {
            "data": user_data,
            "roleIds": role_ids,
            "postIds": post_ids,
            "roles": CamelCaseUtil.transform_result(roles),
            "posts": CamelCaseUtil.transform_result(posts),
        }

    @classmethod
    async def user_detail_services(cls, query_db: AsyncSession, user_id: int):
        """获取用户详情(个人中心)"""
        user_info = await UserDao.get_user_by_id(query_db, user_id)
        user = user_info.get("user_basic_info")
        if user:
            user_data = CamelCaseUtil.transform_result(user)
            # 获取角色名称
            roles = user_info.get("user_role_info", [])
            role_group = ",".join([r.role_name for r in roles]) if roles else ""
            # 获取岗位名称
            posts = user_info.get("user_post_info", [])
            post_group = ",".join([p.post_name for p in posts]) if posts else ""
            return {"data": user_data, "roleGroup": role_group, "postGroup": post_group}
        raise ServiceException(message="用户不存在")

    @classmethod
    async def change_status_services(cls, query_db: AsyncSession, user_model: EditUserModel, current_user_name: str):
        """修改用户状态"""
        update_data = {
            "status": user_model.status,
            "update_by": current_user_name,
            "update_time": datetime.now(),
        }
        await UserDao.update_user(query_db, user_model.user_id, update_data)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message="修改成功")

    @classmethod
    async def reset_pwd_services(cls, query_db: AsyncSession, user_model: EditUserModel, current_user_name: str):
        """重置密码"""
        pwd = user_model.password[:72] if user_model.password and len(user_model.password) > 72 else user_model.password
        update_data = {
            "password": PwdUtil.get_password_hash(pwd),
            "update_by": current_user_name,
            "update_time": datetime.now(),
        }
        await UserDao.update_user(query_db, user_model.user_id, update_data)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message="重置成功")

    @classmethod
    async def update_profile_services(
        cls, query_db: AsyncSession, user_model: EditUserModel, current_user_id: int, current_user_name: str
    ):
        """修改个人信息"""
        update_data = {
            "nick_name": user_model.nick_name,
            "email": user_model.email,
            "phonenumber": user_model.phonenumber,
            "sex": user_model.sex,
            "update_by": current_user_name,
            "update_time": datetime.now(),
        }
        await UserDao.update_user(query_db, current_user_id, update_data)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message="修改成功")

    @classmethod
    async def update_pwd_services(
        cls, query_db: AsyncSession, old_password: str, new_password: str, current_user_id: int, current_user_name: str
    ):
        """修改个人密码"""
        user_info = await UserDao.get_user_by_id(query_db, current_user_id)
        user = user_info.get("user_basic_info")
        if not user:
            raise ServiceException(message="用户不存在")

        if not PwdUtil.verify_password(old_password, user.password):
            raise ServiceException(message="旧密码错误")

        pwd = new_password[:72] if len(new_password) > 72 else new_password
        update_data = {
            "password": PwdUtil.get_password_hash(pwd),
            "update_by": current_user_name,
            "update_time": datetime.now(),
        }
        await UserDao.update_user(query_db, current_user_id, update_data)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message="修改成功")

    @staticmethod
    def build_dept_tree(depts: list, parent_id: int = 0) -> List[dict]:
        """构建部门树形结构"""
        tree = []
        for dept in depts:
            if dept.parent_id == parent_id:
                node = {
                    "id": dept.dept_id,
                    "label": dept.dept_name,
                    "children": UserService.build_dept_tree(depts, dept.dept_id),
                }
                if not node["children"]:
                    del node["children"]
                tree.append(node)
        return tree

    @classmethod
    async def get_dept_tree_services(cls, query_db: AsyncSession):
        """获取部门树结构"""
        depts = await UserDao.get_dept_list_for_tree(query_db)
        tree = cls.build_dept_tree(depts)
        return tree

    @classmethod
    async def get_auth_role_services(cls, query_db: AsyncSession, user_id: int):
        """获取授权角色"""
        user_info = await UserDao.get_user_by_id(query_db, user_id)
        user = user_info.get("user_basic_info")
        if not user:
            raise ServiceException(message="用户不存在")

        roles = await UserDao.get_all_roles(query_db)

        user_role_ids = await UserDao.get_user_role_ids(query_db, user_id)

        processed_roles = []
        for role in roles:
            # If user is not super admin (id=1), do not show super admin role (id=1)
            if user_id != 1 and role.role_id == 1:
                continue

            role_dict = CamelCaseUtil.transform_result(role)
            role_dict["flag"] = role.role_id in user_role_ids
            processed_roles.append(role_dict)

        return {"user": CamelCaseUtil.transform_result(user), "roles": processed_roles}

    @classmethod
    async def update_auth_role_services(cls, query_db: AsyncSession, user_id: int, role_ids: Optional[str]):
        """保存授权角色"""
        if not await UserDao.check_user_allowed(query_db, user_id):
            raise ServiceException(message="不允许操作超级管理员用户")

        # Delete existing
        await UserDao.delete_user_role_by_user_id(query_db, user_id)

        # Add new
        if role_ids:
            ids = role_ids.split(",")
            for role_id in ids:
                if role_id:
                    # Check if trying to assign Super Admin role (role_id=1) to non-admin user
                    if int(role_id) == 1 and user_id != 1:
                        raise ServiceException(message="禁止为其他用户赋予超级管理员角色")

                    user_role = SysUserRole(user_id=user_id, role_id=int(role_id))
                    await UserDao.add_user_role(query_db, user_role)

        await query_db.commit()
        return CrudResponseModel(is_success=True, message="授权成功")

    @classmethod
    async def export_user_services(cls, query_db: AsyncSession, query_params: dict):
        """导出用户列表"""
        query = select(SysUser).where(SysUser.del_flag == "0")
        if query_params.get("user_name"):
            query = query.where(SysUser.user_name.like(f"%{query_params['user_name']}%"))
        if query_params.get("phonenumber"):
            query = query.where(SysUser.phonenumber.like(f"%{query_params['phonenumber']}%"))
        if query_params.get("status"):
            query = query.where(SysUser.status == query_params["status"])
        if query_params.get("dept_id"):
            query = query.where(SysUser.dept_id == query_params["dept_id"])

        users = await UserDao.get_user_list(query_db, query)

        data = []
        for user in users:
            data.append(
                {
                    "用户ID": user.user_id,
                    "用户账号": user.user_name,
                    "用户昵称": user.nick_name,
                    "部门ID": user.dept_id,
                    "手机号码": user.phonenumber,
                    "用户状态": "正常" if user.status == "0" else "停用",
                    "创建时间": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else "",
                }
            )

        df = pd.DataFrame(data)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="用户数据")

        output.seek(0)
        return output

    @classmethod
    async def import_data_services(
        cls, query_db: AsyncSession, file: UploadFile, update_support: bool, current_user_name: str
    ):
        """导入用户数据"""
        try:
            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents))

            success_count = 0
            failure_count = 0
            messages = []

            for index, row in df.iterrows():
                try:
                    user_name = str(row.get("用户账号", "")).strip()
                    if not user_name or user_name == "nan":
                        continue

                    # Check if user exists
                    existing = await UserDao.get_user_by_name(query_db, user_name)

                    # Parse status
                    status_str = str(row.get("用户状态", "正常")).strip()
                    status = "0" if status_str == "正常" else "1"

                    # Parse dept_id
                    dept_id = row.get("部门ID")
                    if pd.isna(dept_id):
                        dept_id = None
                    else:
                        dept_id = int(dept_id)

                    if existing:
                        if not update_support:
                            failure_count += 1
                            messages.append(f"<br/>账号 {user_name} 已存在")
                            continue
                        else:
                            # Update logic
                            update_data = {
                                "nick_name": str(row.get("用户昵称", user_name)),
                                "phonenumber": str(row.get("手机号码", "")),
                                "status": status,
                                "dept_id": dept_id,
                                "update_by": current_user_name,
                                "update_time": datetime.now(),
                            }
                            await UserDao.update_user(query_db, existing.user_id, update_data)
                            success_count += 1
                    else:
                        # Create new user
                        user = SysUser(
                            user_name=user_name,
                            nick_name=str(row.get("用户昵称", user_name)),
                            phonenumber=str(row.get("手机号码", "")),
                            status=status,
                            dept_id=dept_id,
                            create_by=current_user_name,
                            create_time=datetime.now(),
                            password=PwdUtil.get_password_hash("123456"),  # Default password
                        )
                        await UserDao.add_user(query_db, user)
                        success_count += 1
                except Exception as row_error:
                    failure_count += 1
                    messages.append(f"<br/>行 {index + 2} 数据错误: {str(row_error)}")
                    continue

            await query_db.commit()

            msg = f"导入成功 {success_count} 条，失败 {failure_count} 条"
            if messages:
                msg += "".join(messages)

            return {"msg": msg, "messages": messages}

        except Exception as e:
            logger.error(f"导入失败: {str(e)}")
            raise ServiceException(message="导入失败，请检查文件格式")
