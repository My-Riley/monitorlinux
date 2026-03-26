import io

import pandas as pd
from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter
from sqlalchemy.ext.asyncio import AsyncSession

from config.get_db import get_db
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_camera.dao.camera_dao import CameraDao
from module_camera.service.camera_service import CameraService
from utils.log_util import logger
from utils.response_util import ResponseUtil

# 创建路由器，挂载到 /camera/camera 路径下，并添加登录依赖
cameraImportController = APIRouter(
    prefix="/camera/camera", dependencies=[Depends(LoginService.get_current_user)], tags=["摄像头导入"]
)


def row_to_camera_dict(row: pd.Series) -> dict:
    """
    将DataFrame的一行转换为Camera模型所需的字典格式。
    处理空值和NaN。
    """

    def clean_value(val):
        if pd.isna(val) or str(val).strip().lower() in ["nan", "none", ""]:
            return None
        return str(val).strip()

    return {
        "cameraName": clean_value(row.get("摄像头名称")),
        "regionId": clean_value(row.get("区域ID")),  # 注意：模板里是ID，不是名称
        "status": clean_value(row.get("摄像头状态")) or "0",  # 默认开启
        "username": clean_value(row.get("登录账号")),
        "password": clean_value(row.get("登录密码")),
        "cameraIp": clean_value(row.get("摄像头IP")),  # 这是关键字段
        "port": clean_value(row.get("摄像头端口")),
        "rtspPort": clean_value(row.get("RTSP端口")),
        "protocol": clean_value(row.get("RTSP协议路径")),
        "brand": clean_value(row.get("摄像头品牌")),
        "line": clean_value(row.get("线路")) or "0",
    }


@cameraImportController.get("/importTemplate")
async def download_camera_import_template(request: Request):
    """下载摄像头导入模板（仅含表头和填写说明，无示例数据）"""
    try:
        output = io.BytesIO()

        # 模板示例数据（包含2行示例，帮助用户理解填写格式）
        template_data = {
            "摄像头名称": ["dmoe01", "dmoe02", "dmoe03"],
            "区域ID": ["1", "2", "3"],
            "摄像头IP": ["192.168.10.101", "192.168.10.102", "192.168.10.103"],
            "RTSP端口": ["554", "554", "554"],
            "摄像头端口": ["80", "8080", "80"],
            "登录账号": ["admin", "admin", "admin"],
            "登录密码": ["admin123", "123456", "123456"],
            "摄像头品牌": ["海康", "大华", "其他"],
            "RTSP协议路径": ["/Streaming/Channels/1", "/cam/realmonitor?channel=1&subtype=0", ""],
        }

        df = pd.DataFrame(template_data)

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="摄像头信息")
            worksheet = writer.sheets["摄像头信息"]

            # 设置标题样式：加粗 + 居中
            header_font = Font(bold=True)
            header_alignment = Alignment(horizontal="center", vertical="center")
            for cell in worksheet[1]:
                cell.font = header_font
                cell.alignment = header_alignment

            # 自动调整列宽（最小12，最大30）
            for idx, col in enumerate(df.columns, 1):
                max_length = max(len(str(col)), len(str(df[col].iloc[0])) if not pd.isna(df[col].iloc[0]) else 0)
                adjusted_width = min(30, max(12, max_length + 2))
                worksheet.column_dimensions[get_column_letter(idx)].width = adjusted_width

            # 冻结首行，方便滚动时查看标题
            worksheet.freeze_panes = "A2"

            # 启用自动筛选
            worksheet.auto_filter.ref = worksheet.dimensions

        output.seek(0)
        logger.info("下载摄像头导入模板成功")

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment; filename=camera_import_template.xlsx",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as e:
        logger.error(f"下载摄像头导入模板失败: {str(e)}", exc_info=True)
        return ResponseUtil.error(msg=f"下载模板失败: {str(e)}")


@cameraImportController.post("/upload")
async def upload_camera_excel(
    request: Request,
    file: UploadFile = File(...),
    update_support: int = Query(default=0, alias="updateSupport"),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """
    导入摄像头Excel文件

    参数:
        file: Excel文件
        update_support: 是否更新已存在的数据（0=否，1=是）
    """
    try:
        # 1. 验证文件类型
        if not file.filename.endswith((".xlsx", ".xls")):
            return ResponseUtil.error(msg="只支持上传.xlsx或.xls格式的Excel文件")

        # 2. 读取文件内容
        contents = await file.read()
        try:
            df = pd.read_excel(io.BytesIO(contents))
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            return ResponseUtil.error(msg=f"Excel文件格式错误或已损坏: {str(e)}")

        # 3. 检查是否为空文件
        if df.empty:
            return ResponseUtil.error(msg="Excel文件内容为空，请检查文件")

        # 4. 验证必需的列
        required_columns = ["摄像头IP", "摄像头名称", "登录账号", "登录密码", "RTSP端口"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return ResponseUtil.error(msg=f"Excel文件缺少必需的列: {', '.join(missing_columns)}")

        success_count = 0
        failure_count = 0
        duplicate_no_update_count = 0
        failure_msg = []

        # 5. 遍历DataFrame处理每一行
        for index, row in df.iterrows():
            try:
                camera_ip = str(row.get("摄像头IP", "")).strip().replace(" ", "")
                if not camera_ip or camera_ip.lower() == "nan":
                    failure_msg.append(f"第{index + 2}行：摄像头IP为空")
                    failure_count += 1
                    continue

                # 构建新的摄像头数据字典
                new_camera_data = row_to_camera_dict(row)
                # 确保IP是干净的
                new_camera_data["cameraIp"] = camera_ip

                # 6. 检查IP是否已存在
                existing_camera = await CameraDao.get_camera_by_ip(query_db, camera_ip)

                if existing_camera:
                    # 7. IP已存在，根据update_support参数决定是否更新
                    if update_support == 1:
                        # 允许更新，执行更新操作
                        await CameraService.update_camera(
                            query_db, existing_camera.camera_id, new_camera_data, current_user.user.user_name
                        )
                        success_count += 1
                    else:
                        # 不允许更新，记录为重复并跳过
                        duplicate_no_update_count += 1
                        failure_msg.append(
                            f'第{index + 2}行：摄像头IP {camera_ip} 已存在，如需更新请勾选"更新已存在数据"选项'
                        )
                else:
                    # 8. IP不存在，执行新增
                    await CameraService.add_camera(query_db, new_camera_data, current_user.user.user_name)
                    success_count += 1

            except Exception as e:
                error_detail = f"第{index + 2}行：{str(e)}"
                failure_msg.append(error_detail)
                failure_count += 1
                logger.error(f"导入第{index + 2}行数据失败: {str(e)}")

        # 10. 构建返回消息
        msg_parts = [f"成功导入/更新{success_count}条数据"]
        if duplicate_no_update_count > 0:
            msg_parts.append(f"，{duplicate_no_update_count}条因IP重复且无更新被跳过")
        if failure_count > 0:
            msg_parts.append(f"，失败{failure_count}条")
        if failure_msg:
            msg_parts.append("<br/><br/>错误详情：<br/>")
            msg_parts.append("<br/>".join(failure_msg[:10]))
            if failure_count > 10:
                msg_parts.append(f"<br/>...还有{failure_count - 10}条错误未显示")

        msg = "".join(msg_parts)
        logger.info(
            f"导入摄像头Excel完成：成功{success_count}条，重复无更新{duplicate_no_update_count}条，失败{failure_count}条"
        )
        return ResponseUtil.success(msg=msg)

    except Exception as e:
        await query_db.rollback()
        logger.error(f"导入摄像头Excel失败: {str(e)}", exc_info=True)
        return ResponseUtil.error(msg=f"导入失败: {str(e)}")
