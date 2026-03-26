# student_vo.py
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class StudentModel(BaseModel):
    """班级学生信息 Pydantic 模型"""

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    id: Optional[int] = Field(default=None, description="主键")
    student_id: Optional[str] = Field(default=None, description="学号（唯一标识）")
    student_name: Optional[str] = Field(default=None, description="学生姓名")
    classes: Optional[str] = Field(default=None, description="班级")
    email: Optional[str] = Field(default=None, description="邮箱")
    grade: Optional[str] = Field(default=None, description="年级")
    phonenumber: Optional[str] = Field(default=None, description="手机号码")
    sex: Optional[Literal["0", "1", "2"]] = Field(default="2", description="性别（0男 1女 2未知）")
    age: Optional[int] = Field(default=None, description="年龄")
    face_image: Optional[str] = Field(default=None, description="人脸图像")
    status: Optional[Literal["0", "1"]] = Field(default="0", description="状态（0正常 1停用）")
    del_flag: Optional[Literal["0", "2"]] = Field(default="0", description="是否删除（0存在 2删除）")
    create_time: Optional[datetime] = Field(default=None, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    remark: Optional[str] = Field(default=None, description="备注")


class StudentQueryModel(BaseModel):
    """学生分页查询参数"""

    model_config = ConfigDict(populate_by_name=True)

    # 显式为需要驼峰的字段指定 alias
    classes: Optional[str] = Field(None, alias="classes")
    grade: Optional[str] = Field(None, alias="grade")
    student_name: Optional[str] = Field(None, alias="studentName")
    student_id: Optional[str] = Field(None, alias="studentId")
    sex: Optional[str] = Field(None, alias="sex")
    age: Optional[int] = Field(None, alias="age")
    begin_time: Optional[datetime] = Field(None, alias="beginTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    page_num: int = Field(1, alias="pageNum")
    page_size: int = Field(10, alias="pageSize")


class EditStudentModel(BaseModel):
    """新增 / 修改学生"""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    id: Optional[int] = None
    student_id: str = Field(..., description="学号")
    student_name: str = Field(..., description="学生姓名")
    classes: str = Field(..., description="班级")

    grade: Optional[str] = None
    email: Optional[str] = None
    phonenumber: Optional[str] = None
    sex: Optional[Literal["0", "1", "2"]] = "2"
    age: Optional[int] = None
    face_image: Optional[str] = None
    status: Optional[Literal["0", "1"]] = "0"
    remark: Optional[str] = None
