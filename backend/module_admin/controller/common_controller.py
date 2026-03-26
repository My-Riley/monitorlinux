import base64
import os
import uuid

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config.env import UploadConfig
from config.get_db import get_db
from utils.log_util import logger
from utils.response_util import ResponseUtil

commonController = APIRouter(prefix="/common", tags=["通用接口"])

UPLOAD_DIR = UploadConfig.UPLOAD_PATH


@commonController.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    userName: str = Query(default=None, description="学生姓名"),
    studentId: str = Query(default=None, description="学号"),
    query_db: AsyncSession = Depends(get_db),
):
    """通用文件上传接口 - 统一保存到 all_image 文件夹"""
    try:
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"

        # 使用姓名+学号格式命名文件
        if userName and studentId:
            new_filename = f"{userName}{studentId}{file_ext}"
        elif userName:
            new_filename = f"{userName}{file_ext}"
        elif studentId:
            new_filename = f"{studentId}{file_ext}"
        else:
            new_filename = f"{uuid.uuid4().hex}{file_ext}"

        content = await file.read()

        # 将图片保存到 all_image 文件夹
        all_image_dir = os.path.join(UPLOAD_DIR, "all_image")
        if not os.path.exists(all_image_dir):
            os.makedirs(all_image_dir)

        save_path = os.path.join(all_image_dir, new_filename)

        # 如果文件已存在，添加序号
        # 注意：如果指定了姓名和学号，说明是特定学生的头像，直接覆盖（不重命名）
        should_rename = True
        if userName and studentId:
            should_rename = False

        if should_rename and os.path.exists(save_path):
            base_name = new_filename.rsplit(".", 1)[0]
            ext = new_filename.rsplit(".", 1)[1] if "." in new_filename else "jpg"
            counter = 1
            while os.path.exists(save_path):
                new_filename = f"{base_name}_{counter}.{ext}"
                save_path = os.path.join(all_image_dir, new_filename)
                counter += 1

        with open(save_path, "wb") as f:
            f.write(content)

        # 返回 URL (指向 all_image)
        url = f"/profile/all_image/{new_filename}"
        logger.info(f"文件上传成功: {url}")

        return ResponseUtil.success(
            msg="上传成功",
            dict_content={"url": url, "fileName": url, "newFileName": new_filename, "originalFilename": file.filename},
        )
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return ResponseUtil.failure(msg=f"上传失败: {str(e)}")


@commonController.post("/uploadBase64")
async def upload_base64_image(request: Request, query_db: AsyncSession = Depends(get_db)):
    """
    Base64图片上传接口 - 供情绪识别采集端使用
    请求体格式: {"base": "base64字符串", "name": "学生姓名", "studentId": "学号"}
    统一保存到 all_image 文件夹
    """
    try:
        body = await request.json()
        base64_data = body.get("base", "")
        name = body.get("name", "unknown")
        student_id = body.get("studentId", "")

        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        image_data = base64.b64decode(base64_data)

        if student_id:
            filename = f"{name}{student_id}.jpg"
        else:
            filename = f"{name}.jpg"

        # 将图片保存到 all_image 文件夹
        all_image_dir = os.path.join(UPLOAD_DIR, "all_image")
        if not os.path.exists(all_image_dir):
            os.makedirs(all_image_dir)

        save_path = os.path.join(all_image_dir, filename)

        # 如果文件已存在，且不是指定学号的特定文件，则添加序号
        should_rename = True
        if student_id:
            should_rename = False

        if should_rename and os.path.exists(save_path):
            base_name = filename.rsplit(".", 1)[0]
            ext = filename.rsplit(".", 1)[1] if "." in filename else "jpg"
            counter = 1
            while os.path.exists(save_path):
                filename = f"{base_name}_{counter}.{ext}"
                save_path = os.path.join(all_image_dir, filename)
                counter += 1

        with open(save_path, "wb") as f:
            f.write(image_data)

        url = f"/profile/all_image/{filename}"
        logger.info(f"Base64图片上传成功: {url}")

        return ResponseUtil.success(msg=url, dict_content={"url": url, "fileName": url})
    except Exception as e:
        logger.error(f"Base64图片上传失败: {str(e)}")
        return ResponseUtil.failure(msg=f"上传失败: {str(e)}")


@commonController.post("/deleteImage")
async def delete_image(request: Request):
    """
    删除图片文件接口 - 用于删除未保存的图片（如取消新增时）
    删除原始文件和 all_image 文件夹中的副本
    请求体: {"imagePath": "/profile/2501班/学生A202501.jpg"}
    """
    try:
        body = await request.json()
        image_path = body.get("imagePath", "")

        if not image_path:
            return ResponseUtil.error(msg="图片路径不能为空")

        # 从URL路径中提取相对路径（去掉 /profile/ 前缀）
        relative_path = image_path.replace("/profile/", "").strip()
        if not relative_path:
            return ResponseUtil.error(msg="无效的图片路径")

        original_file = os.path.join(UPLOAD_DIR, relative_path)
        deleted_files = []

        # 删除原始文件
        if os.path.exists(original_file):
            os.remove(original_file)
            deleted_files.append(original_file)
            logger.info(f"已删除原始图片文件: {original_file}")

        # 删除 all_image 文件夹中的副本
        filename = os.path.basename(image_path)
        all_image_path = os.path.join(UPLOAD_DIR, "all_image", filename)
        if os.path.exists(all_image_path):
            os.remove(all_image_path)
            deleted_files.append(all_image_path)
            logger.info(f"已删除 all_image 中的图片副本: {all_image_path}")

        if deleted_files:
            return ResponseUtil.success(msg="图片删除成功", dict_content={"deletedFiles": deleted_files})
        else:
            return ResponseUtil.warning(msg="图片文件不存在，可能已被删除")

    except Exception as e:
        logger.error(f"删除图片文件失败: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return ResponseUtil.error(msg=f"删除失败: {str(e)}")
