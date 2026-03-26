import io
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.do.dept_do import SysDept
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from utils.common_util import PwdUtil
from utils.log_util import logger
from utils.response_util import ResponseUtil

userImportController = APIRouter(
    prefix="/system/user", dependencies=[Depends(LoginService.get_current_user)], tags=["用户导入"]
)


@userImportController.post("/upload")
async def upload_user_excel(
    request: Request,
    file: UploadFile = File(...),
    update_support: int = Query(default=0, alias="updateSupport"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """导入用户Excel文件"""
    try:
        # 验证文件类型
        if not file.filename.endswith((".xlsx", ".xls")):
            return ResponseUtil.error(msg="只支持上传.xlsx或.xls格式的Excel文件")

        # 读取文件内容
        contents = await file.read()

        # 尝试读取Excel文件
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            return ResponseUtil.error(msg=f"Excel文件格式错误或已损坏: {str(e)}")

        # 检查是否为空文件
        if df.empty:
            return ResponseUtil.error(msg="Excel文件内容为空，请检查文件")

        # 验证必需的列
        required_columns = ["用户账号", "用户昵称"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ResponseUtil.error(msg=f"Excel文件缺少必需的列: {', '.join(missing_columns)}")

        success_count = 0
        failure_count = 0
        failure_msg = []

        for index, row in df.iterrows():
            try:
                # 提取数据并处理空值
                user_name = str(row.get("用户账号", "")).strip()
                if not user_name or user_name.lower() == "nan":
                    failure_msg.append(f"第{index + 2}行：用户账号为空")
                    failure_count += 1
                    continue

                nick_name = str(row.get("用户昵称", "")).strip()
                if not nick_name or nick_name.lower() == "nan":
                    nick_name = user_name

                # 处理部门名称提取 ID
                dept_name = str(row.get("部门名称", "")).strip()
                dept_id = None
                if dept_name and dept_name.lower() != "nan":
                    dept_query = select(SysDept.dept_id).where(SysDept.dept_name == dept_name, SysDept.del_flag == "0")
                    dept_result = await query_db.execute(dept_query)
                    dept_id = dept_result.scalar()

                # 处理性别
                sex = str(row.get("用户性别", "0")).strip()
                sex_map = {"男": "0", "女": "1", "未知": "2"}
                sex = sex_map.get(sex, sex if sex in ["0", "1", "2"] else "0")

                status = str(row.get("帐号状态", "0")).strip()
                status_map = {"正常": "0", "停用": "1"}
                status = status_map.get(status, "0")

                phonenumber = str(row.get("手机号码", "")).strip()
                if phonenumber.lower() == "nan":
                    phonenumber = ""

                email = str(row.get("用户邮箱", "")).strip()
                if email.lower() == "nan":
                    email = ""

                remark = str(row.get("备注", "")).strip()
                if remark.lower() == "nan":
                    remark = ""

                # 检查用户是否存在
                existing_user = await query_db.execute(
                    select(SysUser).where(SysUser.user_name == user_name, SysUser.del_flag == "0")
                )
                existing_user = existing_user.scalar()

                if existing_user:
                    if update_support == 1:
                        # 更新已存在的用户
                        update_data = {
                            "nick_name": nick_name,
                            "dept_id": dept_id,
                            "email": email,
                            "phonenumber": phonenumber,
                            "sex": sex,
                            "status": status,
                            "remark": remark,
                            "update_by": current_user.user.user_name,
                            "update_time": datetime.now(),
                        }
                        update_stmt = (
                            update(SysUser).where(SysUser.user_id == existing_user.user_id).values(**update_data)
                        )
                        await query_db.execute(update_stmt)
                        success_count += 1
                    else:
                        failure_msg.append(f"第{index + 2}行：用户账号 {user_name} 已存在")
                        failure_count += 1
                else:
                    # 创建新用户，默认密码 123456
                    hashed_password = PwdUtil.get_password_hash("123456")
                    new_user = SysUser(
                        user_name=user_name,
                        nick_name=nick_name,
                        dept_id=dept_id,
                        email=email,
                        phonenumber=phonenumber,
                        sex=sex,
                        status=status,
                        password=hashed_password,
                        remark=remark,
                        del_flag="0",
                        create_by=current_user.user.user_name,
                        create_time=datetime.now(),
                    )
                    query_db.add(new_user)
                    success_count += 1

            except Exception as e:
                failure_msg.append(f"第{index + 2}行：{str(e)}")
                failure_count += 1
                logger.error(f"导入第{index + 2}行用户失败: {str(e)}")

        await query_db.commit()

        msg_parts = [f"成功导入{success_count}条用户数据"]
        if failure_count > 0:
            msg_parts.append(f"，失败{failure_count}条")
            if failure_msg:
                msg_parts.append("<br/><br/>错误详情：<br/>")
                msg_parts.append("<br/>".join(failure_msg[:10]))

        return ResponseUtil.success(msg="".join(msg_parts))

    except Exception as e:
        await query_db.rollback()
        logger.error(f"导入用户Excel失败: {str(e)}")
        return ResponseUtil.error(msg=f"导入失败: {str(e)}")


@userImportController.get("/importTemplate")
async def download_import_template(request: Request):
    """下载用户导入模板"""
    output = io.BytesIO()

    template_data = {
        "用户账号": ["admin_test", "ry_test"],
        "用户昵称": ["测试管理员", "测试人员"],
        "部门名称": ["研发部门", "测试部门"],
        "用户邮箱": ["test@163.com", "ry@163.com"],
        "手机号码": ["15888888888", "15666666666"],
        "用户性别": ["男", "女"],
        "帐号状态": ["正常", "正常"],
        "备注": ["系统导入用户", ""],
    }
    df = pd.DataFrame(template_data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="用户信息")
        worksheet = writer.sheets["用户信息"]

        # 设置列宽
        col_widths = {"A": 15, "B": 15, "C": 20, "D": 25, "E": 15, "F": 10, "G": 10, "H": 30}
        for col, width in col_widths.items():
            worksheet.column_dimensions[col].width = width

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=user_import_template.xlsx",
            "Access-Control-Expose-Headers": "Content-Disposition",
        },
    )
