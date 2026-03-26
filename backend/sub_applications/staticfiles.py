import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.env import UploadConfig
from utils.log_util import logger


def mount_staticfiles(app: FastAPI):
    """挂载静态文件"""
    # 使用配置文件中的上传路径
    upload_dir = UploadConfig.UPLOAD_PATH
    upload_prefix = UploadConfig.UPLOAD_PREFIX

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    # 获取绝对路径
    abs_upload_dir = os.path.abspath(upload_dir)
    logger.info(f"🔎 挂载静态文件: {upload_prefix} -> {abs_upload_dir}")

    app.mount(upload_prefix, StaticFiles(directory=upload_dir), name="profile")
    logger.info("✅️ 静态文件挂载成功")
