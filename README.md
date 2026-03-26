# 情绪识别监控系统 (Emotion Monitor)

> 基于 RuoYi-Vue-FastAPI 架构的高性能校园情绪监控与心理预警平台。

[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-2.6+-4FC08D.svg?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-6.0+-DC382D.svg?style=flat&logo=redis&logoColor=white)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

**情绪识别监控系统** 是一套专为校园场景设计的心理健康监测平台。系统通过部署在校园各处的摄像头，实时采集学生的表情数据，利用先进的深度学习算法进行情绪识别与焦虑分析。系统集成了大屏可视化、设备管理、预警推送及人像库管理等功能，为学校提供科学、高效的心理健康管理方案。

### 🌟 核心特性

*   **实时情绪识别**：支持 8 种基础情绪（如喜悦、中性、愤怒、悲伤等）的高精度识别。
*   **多维焦虑分析**：自动将情绪数据映射为 4 级焦虑状态（无、低、中、高），提供直观的心理状态指引。
*   **采集端解耦**：独立的 `emotion_analysis` 采集服务，支持多摄像头并发处理。
*   **RuoYi 赋予的强大后台**：基于 RuoYi-Vue-FastAPI，拥有完善的角色权限、字典管理及日志系统。
*   **可视化驾驶舱**：提供班级、科目、地点等多维度的 ECharts 动态统计图表。

---

## 📐 系统架构

系统采用分层微服务架构，从前端展示到数据采集形成完整的闭环。整体架构包含以下层次：

### 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                     前端展示层 (Frontend Layer)               │
│                   Vue.js + Element UI                        │
│              (大屏可视化、设备管理、数据统计)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                   后端服务层 (Backend Layer)                 │
│                    FastAPI 0.116                            │
│         (RESTful API、权限管理、业务逻辑处理)                 │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
    ┌──────▼──────┐                ┌──────▼──────┐
    │ Redis Cache │                │  MySQL DB   │
    │   (缓存层)  │                │  (数据持久化)│
    └──────┬──────┘                └─────────────┘
           │
           │ 消息队列/缓存访问
    ┌──────▼──────────────────────────────────────────┐
    │           专业化服务层 (Service Layer)            │
    ├──────────────────────────────────────────────────┤
    │  • 情绪分析服务 (emotion_analysis)               │
    │  • 摄像头预览服务 (camera_frontend_preview)      │
    │  • RTSP 流处理服务                               │
    └──────────────────────────────────────────────────┘
                            │
    ┌───────────────────────▼─────────────────────────┐
    │              数据采集层 (Data Collection)        │
    │            RTSP 摄像头流 + 深度学习模型          │
    └─────────────────────────────────────────────────┘
```

### 组件说明

| 层级 | 组件 | 职责 | 技术实现 |
|:---|:---|:---|:---|
| **前端层** | Vue.js 前端界面 | 用户交互、数据可视化、设备管理 | Vue 2.6 + Element UI + ECharts |
| **后端层** | FastAPI 后端 API | RESTful 接口、权限验证、业务逻辑 | FastAPI + SQLAlchemy + RuoYi 权限体系 |
| **数据层** | MySQL 数据库 | 持久化存储（用户、设备、情绪数据） | MySQL 8.0 |
| **缓存层** | Redis 缓存 | 会话管理、权限缓存、高频数据缓存 | Redis 6.0 |
| **服务层** | 情绪分析服务 | 实时情绪识别与数据采集 | Python + OpenCV + 深度学习模型 |
| **服务层** | 摄像头预览服务 | RTSP 流转 MJPEG 供浏览器预览 | Python + OpenCV |
| **数据源** | RTSP 摄像头流 | 实时视频流采集 | RTSP 协议 |

### 数据流向

1. **采集流程**：RTSP 摄像头流 → 情绪分析服务 → Redis 缓存 → FastAPI 后端 → MySQL 数据库
2. **查询流程**：前端界面 → FastAPI 后端 → (Redis 缓存 / MySQL 数据库) → 前端展示
3. **预览流程**：RTSP 摄像头流 → 摄像头预览服务 → MJPEG 流 → 前端浏览器

### 核心特性

* **解耦设计**：采集服务与业务系统解耦，支持独立部署与扩展
* **异步处理**：FastAPI 异步框架 + SQLAlchemy 异步 ORM，提升并发性能
* **缓存优化**：Redis 缓存权限信息与高频查询数据，降低数据库压力
* **微服务化**：情绪分析、视频预览等专业化服务可独立扩展与维护

---

## 🛠️ 技术栈

| 领域 | 技术方案 | 说明 |
| :--- | :--- | :--- |
| **后端** | FastAPI 0.116 | 高性能异步 Python 框架 |
| **前端** | Vue 2.6 + Element UI | 成熟稳定的中后台前端解决方案 |
| **算法** | face_recognition + OpenCV | 工业级人像比对与视频流处理 |
| **数据库** | MySQL 8.0 | 业务数据持久化 |
| **缓存** | Redis 6.0 | 权限校验与高频数据缓存 |
| **ORM** | SQLAlchemy 2.0 | 异步数据库驱动与模型管理 |

---

## 📂 目录结构

```text
monitorlinux/
├── backend/                # [核心] FastAPI 后端服务
│   ├── module_admin/       # 系统管理模块 (用户/权限/日志)
│   ├── module_camera/      # 业务逻辑模块 (摄像头/情绪数据/预警/课程)
│   ├── config/             # 系统环境与数据库配置
│   └── sql/                # 数据库初始化脚本
├── frontend/               # [核心] Vue 2 前端界面
│   ├── src/api/            # 接口定义
│   └── src/views/          # 页面组件 (含大屏统计)
├── camera_frontend_preview/ # [服务] 摄像头预览服务
│   ├── rtsp_stream_opencv.py # RTSP 流转 MJPEG 服务
│   └── config.ini          # 预览服务运行配置
├── emotion_analysis/       # [算法] 采集端 Python 服务
│   ├── qxsbapi-vl.py       # 情绪识别模型 API 服务
│   ├── emotional.py        # 核心推断程序
│   └── config.ini          # 采集端运行配置
└── docker-compose.my.yml   # 容器化一键部署配置
```

---

## 📊 数据库设计 (共 28 张表)

系统核心由 28 张数据库表支撑，涵盖了权限管理、基础数据及核心业务。

### 核心业务表

| 表名 | 说明 | 核心字段 |
| :--- | :--- | :--- |
| `sys_emotion_result` | 情绪识别结果 | `student_name`, `student_id`, `emotion`, `create_time` |
| `sys_emotion_anxiety_mapping` | 情绪-焦虑映射 | `emotion_en`, `anxiety_level` |
| `sys_camera` | 摄像头设备管理 | `ip_addr`, `brand`, `rtsp_port` |
| `sys_class_student` | 班级学生信息 | `student_id`, `student_name`, `classes`, `face_image` |
| `sys_course` | 课程排班表 | `course_name`, `subject_name`, `course_date` |

### 系统管理表 (RuoYi 基础)

| 权限/配置 | 字典/日志 | 关联表 |
| :--- | :--- | :--- |
| `sys_dept`, `sys_role`, `sys_menu` | `sys_dict_type`, `sys_dict_data` | `sys_user_role`, `sys_role_menu` |
| `sys_config`, `sys_post` | `sys_logininfor`, `sys_oper_log` | `sys_role_dept`, `sys_user_post` |
| `sys_semester`, `sys_semester_cycle` | - | - |

---

## 🚀 快速开始

### 1. 环境准备

- **Python**: 3.10+ (推荐使用 Conda 虚拟环境)
- **Node.js**: 14+ (推荐 v16)
- **MySQL**: 8.0+
- **Redis**: 6.0+

### 2. 数据库部署

1. 创建数据库 `monitor`:
   ```sql
   CREATE DATABASE monitor CHARACTER SET utf8mb4;
   ```
2. 导入数据脚本:
   ```bash
   mysql -u root -p monitor < backend/sql/monitor.sql
   ```

### 3. 后端启动 (backend)

```bash
cd backend
# 创建conda环境
conda create --name emotion_analysis python=3.10
# 激活环境
conda activate emotion_analysis
# 安装其他依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 启动后端
python app.py --env=dev
```

### 4. 前端启动 (frontend)

```bash
cd frontend
# 安装依赖
npm install --registry=https://registry.npmmirror.com
# 启动前端
npm run dev
```
*访问地址：`http://localhost:80` | 默认账号: `admin` / `admin123`*

### 5. 视频预览服务启动 (camera_frontend_preview)

该服务用于将 RTSP 流转为 MJPEG 流以供浏览器预览。
```bash
cd camera_frontend_preview
# 启动前端推流服务
python rtsp_stream_opencv.py
```

### 6. 配置人脸数据

将已知人员的人脸照片放入 `all_image` 目录,文件命名格式为: `姓名+学号.jpeg`

例如: `学生A202401.jpeg`

系统会自动加载这些照片进行人脸匹配。


### 7. 采集端运行 (emotion_analysis)

详细配置请参考 `emotion_analysis/config.ini`。
```bash
cd emotion_analysis
# 1.先启动模型API
python qxsbapi-vl.py
# 2.再启动采集端
python emotional.py
```

### 8. 进程无法启动

若遇到进程占用或无法启动，可使用以下命令：

```bash
# 查看 Python 进程
ps -ef | grep python

# 手动清理采集端进程
pkill -9 -f "emotional.py"
```

---

## 📄 部署文档

Word 格式部署说明（可用 Microsoft Word 打开并另存为 .docx）：[docs/部署文档.html](docs/部署文档.html)

---

## 🐳 Docker 一键部署

系统支持 Docker Compose 部署，适合生产环境：

```bash
docker-compose -f docker-compose.my.yml up -d
```

---

## 🐧 Linux Systemd 自启动配置

生产环境建议使用 Systemd 管理服务，包含 **大模型服务** (`vllm.service`) 和 **业务应用服务** (`emotion-apps.service`)。

### 1. 大模型服务 (vllm.service)

创建 `/etc/systemd/system/vllm.service`，负责启动 Qwen3-VL 大模型：

```ini
[Unit]
Description=Qwen3-VL-4B vLLM Inference Service
After=network.target syslog.target

[Service]
Type=simple
User=root
# 环境变量 (根据实际环境调整 CUDA 路径)
Environment="TORCH_CUDA_ARCH_LIST=11.0a"
Environment="TRITON_PTXAS_PATH=/usr/local/cuda-13.0/bin/ptxas"
Environment="PATH=/data/uv_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# 启动命令 (请修改模型路径 --model)
ExecStart=/data/uv_env/bin/vllm serve "/data/models/Qwen3-VL-4B-Instruct-wt-20260122" \
    --async-scheduling \
    --served-model-name Qwen3-VL-4B-Instruct \
    --port 8000 \
    --host 0.0.0.0 \
    --trust-remote-code \
    --swap-space 16 \
    --max-num-seqs 64 \
    --gpu-memory-utilization 0.60 \
    --enable-prefix-caching

Restart=always
RestartSec=5
StandardOutput=append:/data/vllm_service.log
StandardError=append:/data/vllm_service.log

[Install]
WantedBy=multi-user.target
```

### 2. 业务启动脚本

创建脚本 `/data/qxsb/start_emotion_services.sh`，实现"等待模型就绪 -> 启动业务"逻辑：

```bash
#!/bin/bash
# 配置区：请修改 Python 路径和项目根目录
PYTHON_EXEC="/path/to/your/conda/envs/emotion_analysis/bin/python"
BASE_DIR="/data/qxsb/qxsb_20260129_v1"

echo "[$(date)] 等待 vLLM 服务 (端口 8000)..."
until curl -s http://127.0.0.1:8000/health > /dev/null; do
    echo "vLLM loading..."
    sleep 3
done
echo "vLLM 就绪，启动业务..."

# 1. 启动 Web 后台
cd "${BASE_DIR}/backend"
ln -sf .env.prod .env
$PYTHON_EXEC app.py --env=prod > ../app.log 2>&1 &

# 2. 启动情绪识别 API
cd "${BASE_DIR}/emotion_analysis"
$PYTHON_EXEC qxsbapi-vl.py > ../api.log 2>&1 &

# 3. 启动情绪识别主程序 (前台运行)
echo "启动情绪识别服务..."
$PYTHON_EXEC emotional.py > ../emotional.log 2>&1
```
*注意：执行 `sudo chmod +x /data/qxsb/start_emotion_services.sh` 赋予执行权限。*

### 3. 业务服务 (emotion-apps.service)

创建 `/etc/systemd/system/emotion-apps.service`：

```ini
[Unit]
Description=Emotion Analysis Application Services
After=network.target vllm.service
Requires=vllm.service

[Service]
Type=simple
User=root
WorkingDirectory=/data/qxsb/qxsb_20260129_v1/
ExecStart=/data/qxsb/start_emotion_services.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. 常用管理命令

```bash
# 启用开机自启
sudo systemctl daemon-reload
sudo systemctl enable vllm.service emotion-apps.service

# 启动服务
sudo systemctl start vllm.service
# (确认 vLLM 启动无误后)
sudo systemctl start emotion-apps.service

# 查看状态与日志
sudo systemctl status vllm.service
tail -f /data/vllm_service.log
```

---

## 📈 情绪映射逻辑

| 情绪 (CN) | 焦虑等级 | 等级名称 |
| :--- | :--- | :--- |
| 喜悦, 正常 | 0 | 无焦虑 |
| 藐视, 惊讶 | 1 | 低度焦虑 |
| 愤怒, 厌恶 | 2 | 中度焦虑 |
| 恐惧, 悲伤 | 3 | 高度焦虑 |

---

## ❓ 常见问题 FAQ

> [!TIP]
> **Q: 采集端无法启动？**
> A: 请确保已安装 `ffmpeg` 且 OpenCV 能正常拉取 RTSP 流。
>
> **Q: 验证码不显示？**
> A: 检查 Redis 服务是否在线，及 `.env.dev` 中的 Redis 数据库编号是否冲突。

---

## 🛠️ 维护与监控

### 日志清理

```bash
# 定期清理日志(建议配置logrotate)
sudo truncate -s 0 emotion_analysis/log/daemon.log
sudo truncate -s 0 emotion_analysis/log/daemon.error.log
```

### 数据库备份

```bash
# 备份MySQL数据
mysqldump -u root -p monitor > backup_$(date +%Y%m%d).sql
```

### 监控服务状态

建议使用 `systemd` 或 `supervisor` 管理服务，确保服务自动重启。

---

## 📅 版本与维护

- **当前版本**: v1.0.0
- **更新日期**: 2026-02-02
- **维护**: [Your Name/Dept]

---

> [!IMPORTANT]
> 本项目仅用于校园心理健康科学研究，使用请遵守隐私保护相关法律法规。
