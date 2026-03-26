from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.env import AppConfig
from config.get_db import init_create_table
from config.get_redis import RedisUtil
from config.get_scheduler import SchedulerUtil
from exceptions.handle import handle_exception
from middlewares.handle import handle_middleware
from module_admin.controller.admin_controller import adminController
from module_admin.controller.cache_controller import cacheController
from module_admin.controller.captcha_controller import captchaController
from module_admin.controller.class_student_controller import studentController
from module_admin.controller.class_student_import_controller import studentImportController
from module_admin.controller.common_controller import commonController
from module_admin.controller.config_controller import configController
from module_admin.controller.dept_controller import deptController
from module_admin.controller.dict_controller import dictDataController, dictTypeController
from module_admin.controller.job_controller import jobController
from module_admin.controller.job_log_controller import jobLogController
from module_admin.controller.login_controller import loginController
from module_admin.controller.menu_controller import menuController
from module_admin.controller.monitor_controller import logininforController, operlogController
from module_admin.controller.notice_controller import noticeController
from module_admin.controller.online_controller import onlineController
from module_admin.controller.post_controller import postController
from module_admin.controller.role_controller import roleController
from module_admin.controller.server_controller import serverController
from module_admin.controller.tool_controller import genController
from module_admin.controller.user_controller import userController
from module_admin.controller.websocket_controller import websocketController
from module_camera.controller.camera_controller import cameraController
from module_camera.controller.camera_import_controller import cameraImportController
from module_camera.controller.camera_region_controller import regionController
from module_camera.controller.camera_warn_controller import warnController
from module_camera.controller.course_controller import router as courseController
from module_camera.controller.course_import_controller import courseImportController
from module_camera.controller.emotion_result_controller import emotionController
from module_camera.controller.semester_controller import router as semesterController
from sub_applications.handle import handle_sub_applications
from utils.common_util import worship
from utils.log_util import logger


# 生命周期事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"⏰️ {AppConfig.app_name}开始启动")
    await init_create_table()
    app.state.redis = await RedisUtil.create_redis_pool()
    await RedisUtil.init_sys_dict(app.state.redis)
    await RedisUtil.init_sys_config(app.state.redis)
    await SchedulerUtil.init_system_scheduler()
    logger.info(f"🚀 {AppConfig.app_name}启动成功")
    worship()
    yield
    await RedisUtil.close_redis_pool(app)
    await SchedulerUtil.close_system_scheduler()


# 初始化FastAPI对象
app = FastAPI(
    title=AppConfig.app_name,
    description=f"{AppConfig.app_name}接口文档",
    version=AppConfig.app_version,
    lifespan=lifespan,
    # 修复 root_path 导致的文档加载问题
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 挂载子应用
handle_sub_applications(app)
# 加载中间件处理方法
handle_middleware(app)
# 加载全局异常处理方法
handle_exception(app)


# 加载路由列表
controller_list = [
    {"router": loginController, "tags": ["登录模块"]},
    {"router": captchaController, "tags": ["验证码模块"]},
    {"router": studentImportController, "tags": ["学生导入"]},
    {"router": userController, "tags": ["用户管理"]},
    {"router": adminController, "tags": ["管理员用户管理"]},
    {"router": studentController, "tags": ["班级学生管理"]},
    {"router": deptController, "tags": ["部门管理"]},
    {"router": roleController, "tags": ["角色管理"]},
    {"router": postController, "tags": ["岗位管理"]},
    {"router": menuController, "tags": ["菜单管理"]},
    {"router": dictTypeController, "tags": ["字典类型管理"]},
    {"router": dictDataController, "tags": ["字典数据管理"]},
    {"router": configController, "tags": ["参数配置管理"]},
    {"router": noticeController, "tags": ["通知公告管理"]},
    {"router": operlogController, "tags": ["操作日志"]},
    {"router": logininforController, "tags": ["登录日志"]},
    {"router": onlineController, "tags": ["在线用户"]},
    {"router": jobController, "tags": ["定时任务"]},
    {"router": jobLogController, "tags": ["定时任务日志"]},
    {"router": serverController, "tags": ["服务器监控"]},
    {"router": cacheController, "tags": ["缓存监控"]},
    {"router": cameraImportController, "tags": ["摄像头导入"]},
    {"router": cameraController, "tags": ["摄像头管理"]},
    {"router": emotionController, "tags": ["情绪识别管理"]},
    {"router": courseImportController, "tags": ["课程导入"]},
    {"router": courseController, "tags": ["课程管理"]},
    {"router": semesterController, "tags": ["学期管理"]},
    {"router": regionController, "tags": ["摄像头区域管理"]},
    {"router": warnController, "tags": ["摄像头预警管理"]},
    {"router": commonController, "tags": ["通用接口"]},
    {"router": genController, "tags": ["代码生成"]},
]

for controller in controller_list:
    app.include_router(router=controller.get("router"), tags=controller.get("tags"))

# 注册WebSocket路由
app.include_router(websocketController)

# 静态文件目录已在 sub_applications/staticfiles.py 中挂载
