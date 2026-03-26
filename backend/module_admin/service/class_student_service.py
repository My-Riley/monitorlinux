# module_admin/service/student_service.py
import base64
import logging
import os
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from config.env import UploadConfig
from module_admin.controller.class_student_import_controller import save_image_to_file
from module_admin.dao.class_student_dao import StudentDao
from module_admin.entity.do.class_student_do import SysClassStudent
from module_admin.entity.vo.class_student_vo import EditStudentModel, StudentModel, StudentQueryModel
from utils.page_util import PageResponseModel

logger = logging.getLogger(__name__)


def fix_image_path_if_mismatch(
    face_image_url: Optional[str], student_id: str, student_name: str, classes: Optional[str]
) -> Optional[str]:
    """
    检查图片路径是否与当前学生信息匹配，如果不匹配则重新处理图片路径
    返回修正后的图片路径，如果无需修正则返回原路径
    """
    if not face_image_url:
        return None

    try:
        # 从URL路径中提取相对路径（去掉 /profile/ 前缀）
        relative_path = face_image_url.replace("/profile/", "").strip()
        if not relative_path:
            return None

        # 解析当前路径中的信息
        path_parts = relative_path.split("/")
        if len(path_parts) < 2:
            return face_image_url  # 路径格式异常，保持原样

        current_class_dir = path_parts[0]
        filename = path_parts[-1]

        needs_fix = False

        if current_class_dir != "all_image":
            logger.info(f"图片不在 all_image 目录下: 当前={current_class_dir}")
            needs_fix = True

        # 检查文件名是否匹配（严格匹配，不允许后缀）
        # 获取不带扩展名的文件名
        current_base_name = os.path.splitext(filename)[0]
        expected_base_name = f"{student_name}{student_id}"

        if current_base_name != expected_base_name:
            logger.info(f"图片路径文件名不匹配: 当前={filename}, 期望={expected_base_name}.jpg/png")
            needs_fix = True

        if not needs_fix:
            return face_image_url

        # 需要修正：读取旧图片，重新保存
        old_full_path = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)
        if not os.path.exists(old_full_path):
            logger.warning(f"旧图片文件不存在: {old_full_path}，无法修正路径")
            return None

        with open(old_full_path, "rb") as f:
            image_data = f.read()

        # 删除旧图片文件（包括 all_image 副本）
        try:
            os.remove(old_full_path)
            logger.info(f"已删除旧图片文件: {old_full_path}")

            all_image_path = os.path.join(UploadConfig.UPLOAD_PATH, "all_image", filename)
            if os.path.exists(all_image_path):
                os.remove(all_image_path)
                logger.info(f"已删除 all_image 中的图片副本: {all_image_path}")
        except Exception as e:
            logger.warning(f"删除旧图片失败（继续保存新图片）: {e}")

        # 重新保存图片到正确位置
        new_url = save_image_to_file(
            image_data=image_data,
            student_id=str(student_id),
            student_name=student_name,
            old_student_id=None,  # 已手动删除旧图片，不需要再删除
            old_student_name=None,
        )

        if new_url:
            logger.info(f"图片路径已修正: {face_image_url} -> {new_url}")
            return new_url
        else:
            logger.error("重新保存图片失败，保留原路径")
            return face_image_url

    except Exception as e:
        logger.error(f"修正图片路径失败: {str(e)}", exc_info=True)
        return face_image_url  # 出错时保留原路径


def delete_student_face_image(face_image_url: Optional[str]):
    """删除人脸图片文件（包括原始文件和 all_image 文件夹中的副本）"""
    if not face_image_url:
        return

    try:
        # 可能有多张图片，用逗号分隔
        for img_path in face_image_url.split(","):
            img_path = img_path.strip()
            if not img_path:
                continue

            # 从URL路径中提取相对路径（去掉 /profile/ 前缀）
            relative_path = img_path.replace("/profile/", "")
            original_file = os.path.join(UploadConfig.UPLOAD_PATH, relative_path)

            # 删除原始文件
            if os.path.exists(original_file):
                os.remove(original_file)
                logger.info(f"已删除原始图片文件: {original_file}")
            else:
                logger.warning(f"原始图片文件不存在: {original_file}")

            # 删除 all_image 文件夹中的副本
            filename = os.path.basename(img_path)

            # 新的班级目录结构: upload_path/all_image/文件名
            all_image_path = os.path.join(UploadConfig.UPLOAD_PATH, "all_image", filename)
            if os.path.exists(all_image_path):
                os.remove(all_image_path)
                logger.info(f"已删除 all_image 中的图片副本: {all_image_path}")

            # 兼容旧的日期目录结构: upload_path/年/月/all_image/文件名
            path_parts = relative_path.split("/")
            if len(path_parts) >= 3 and path_parts[0].isdigit() and path_parts[1].isdigit():
                old_all_image_path = os.path.join(
                    UploadConfig.UPLOAD_PATH, path_parts[0], path_parts[1], "all_image", filename
                )
                if os.path.exists(old_all_image_path):
                    os.remove(old_all_image_path)
                    logger.info(f"已删除 all_image 中的图片副本（旧结构）: {old_all_image_path}")

    except Exception as e:
        logger.error(f"删除学生图片文件失败: {str(e)}", exc_info=True)


class StudentService:
    """学生业务服务层"""

    @classmethod
    async def get_student_list(cls, db: AsyncSession, query: StudentQueryModel):
        """
        学生分页列表
        """
        total, items = await StudentDao.select_page(
            db,
            filters=query.model_dump(exclude={"page_num", "page_size"}),
            page_num=query.page_num,
            page_size=query.page_size,
        )

        return PageResponseModel(
            total=total,
            rows=[StudentModel.model_validate(i) for i in items],
            pageNum=query.page_num,
            pageSize=query.page_size,
        )

    @classmethod
    async def get_distinct_classes(cls, db: AsyncSession) -> List[str]:
        return await StudentDao.get_distinct_classes(db)

    @classmethod
    async def get_distinct_grades(cls, db: AsyncSession) -> List[str]:
        return await StudentDao.get_distinct_grades(db)

    @classmethod
    async def search_students_by_keyword(cls, db: AsyncSession, keyword: str) -> List[dict]:
        students = await StudentDao.get_student_by_name(db, keyword)
        return [
            {"studentId": str(s.student_id), "studentName": s.student_name, "classes": s.classes, "grade": s.grade}
            for s in students
        ]

    @classmethod
    async def add_student(cls, db: AsyncSession, data: EditStudentModel, username: str):
        # 学号唯一校验
        exists = await StudentDao.get_student_by_id(db, data.student_id)
        if exists:
            raise ValueError("学号已存在")

        # 检查并修正图片路径（如果图片路径与当前信息不匹配）
        face_image_to_save = data.face_image
        if face_image_to_save:
            face_image_to_save = fix_image_path_if_mismatch(
                face_image_url=face_image_to_save,
                student_id=str(data.student_id),
                student_name=data.student_name,
                classes=data.classes,
            )

        student = SysClassStudent(
            student_id=data.student_id,
            student_name=data.student_name,
            classes=data.classes,
            grade=data.grade,
            sex=data.sex,
            age=data.age,
            face_image=face_image_to_save,
            status="0",
            del_flag="0",
            create_by=username,
            create_time=datetime.now(),
        )

        await StudentDao.insert_student(db, student)

    @classmethod
    async def update_student(cls, db: AsyncSession, db_id: int, data: EditStudentModel, username: str):
        exists = await StudentDao.get_student_by_db_id(db, db_id)
        if not exists:
            raise ValueError("学生不存在")

        # 学号唯一性校验（排除自己）
        if data.student_id != exists.student_id:
            other = await StudentDao.get_student_by_student_id(db, data.student_id)
            if other:
                raise ValueError("该学号已被其他学生使用")

        # === 图片处理逻辑 ===
        face_image_to_save = data.face_image  # 默认使用前端传的值

        # 情况1: 前端上传了新图片（base64）
        if data.face_image and data.face_image.startswith("data:image"):
            try:
                header, encoded = data.face_image.split(",", 1)
                image_data = base64.b64decode(encoded)
                new_url = save_image_to_file(
                    image_data=image_data,
                    student_id=str(data.student_id),
                    student_name=data.student_name,
                    old_student_id=str(exists.student_id),
                    old_student_name=exists.student_name,
                )
                face_image_to_save = new_url
            except Exception as e:
                logger.error(f"解析 base64 图片失败: {e}")
                face_image_to_save = None

        # 情况2: 前端上传了新图片（URL路径），且与原图不同
        elif data.face_image and data.face_image.startswith("/profile/") and data.face_image != exists.face_image:
            # 此时前端已通过 upload 接口上传了新图片并拿到了 URL
            # 我们直接信任这个 URL，因为 upload 接口已经按照当前表单的 studentId 重命名了文件
            face_image_to_save = data.face_image
            logger.info(f"更新学生图片URL: {exists.face_image} -> {data.face_image}")

            # 尝试删除旧图片（如果存在）
            if exists.face_image and exists.face_image != data.face_image:
                try:
                    delete_student_face_image(exists.face_image)
                except Exception as e:
                    logger.warning(f"删除旧图片失败: {e}")

            # 删除旧图后，尝试修正新图片的名称（如果新图片带了_1等后缀，且标准名位置已空出）
            # 注意：只有在 face_image_to_save 有效时才进行
            if face_image_to_save:
                try:
                    face_image_to_save = fix_image_path_if_mismatch(
                        face_image_url=face_image_to_save,
                        student_id=str(data.student_id),
                        student_name=data.student_name,
                        classes=data.classes,
                    )
                except Exception as e:
                    logger.warning(f"修正图片路径失败: {e}")

        # 情况3: 基本信息变了，但没传新图 → 尝试迁移旧图
        elif (
            data.student_id != exists.student_id
            or data.student_name != exists.student_name
            or data.classes != exists.classes
        ) and exists.face_image:
            # 解析旧图片路径
            old_rel_path = exists.face_image.lstrip("/profile/")
            old_full_path = os.path.join(UploadConfig.UPLOAD_PATH, old_rel_path)
            if os.path.exists(old_full_path):
                try:
                    with open(old_full_path, "rb") as f:
                        img_data = f.read()
                    new_url = save_image_to_file(
                        image_data=img_data,
                        student_id=str(data.student_id),
                        student_name=data.student_name,
                        old_student_id=str(exists.student_id),
                        old_student_name=exists.student_name,
                    )
                    face_image_to_save = new_url
                except Exception as e:
                    logger.error(f"迁移旧图片失败: {e}")
                    # 保留原路径（虽然可能已失效）
                    face_image_to_save = exists.face_image
            else:
                # 旧图已丢失，清空
                face_image_to_save = None

        # 情况3: 信息没变 → 保留原图
        else:
            face_image_to_save = exists.face_image

        # 构造更新数据
        update_data = {
            "student_id": data.student_id,
            "student_name": data.student_name,
            "classes": data.classes,
            "grade": data.grade,
            "sex": data.sex,
            "age": data.age,
            "face_image": face_image_to_save,
            "update_by": username,
            "update_time": datetime.now(),
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}

        await StudentDao.update_student_by_id(db, db_id, update_data)

    @classmethod
    async def delete_student(cls, db: AsyncSession, student_id: int):
        """
        按学号 student_id 删除学生（软删除），并清理对应图片文件
        """
        logger.info(f"开始删除学生学号 {student_id}")
        student = await StudentDao.get_student_by_student_id(db, str(student_id))
        if student:
            logger.info(f"找到学生学号 {student_id} 的记录")
            if student.face_image:
                logger.info(f"学生学号 {student_id} 的图片路径为: {student.face_image}")
                delete_student_face_image(student.face_image)
            else:
                logger.info(f"学生学号 {student_id} 没有关联的图片")
        else:
            logger.warning(f"未找到学生学号 {student_id} 的记录")

        await StudentDao.delete_student(db, str(student_id))
        logger.info(f"学生学号 {student_id} 已标记为删除")

    @classmethod
    async def batch_delete_students(cls, db: AsyncSession, student_ids: list[str]):
        """
        按学号 student_id 批量删除学生（软删除），并清理对应图片文件
        """
        # 批量查询学生信息（用于删除前获取 face_image）
        students = await StudentDao.get_students_by_student_ids(db, student_ids)
        for student in students:
            if student.face_image:
                delete_student_face_image(student.face_image)
        await StudentDao.batch_delete_students(db, student_ids)
