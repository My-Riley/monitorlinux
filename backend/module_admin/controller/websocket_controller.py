from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from utils.log_util import logger

websocketController = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接成功，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket断开连接，当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """广播消息给所有连接的客户端"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass


# 全局连接管理器实例
manager = ConnectionManager()


@websocketController.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket端点 - 用于实时消息推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息（保持连接活跃）
            data = await websocket.receive_text()
            # 可以在这里处理客户端发送的消息
            # 例如：心跳检测
            if data == "ping":
                await manager.send_personal_message("pong", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
        manager.disconnect(websocket)


async def notify_warn_update():
    """通知所有客户端预警更新"""
    await manager.broadcast("warn_update")


@websocketController.post("/notify/result")
async def notify_result_update_endpoint():
    """接收内部通知并广播检测结果更新"""
    await manager.broadcast("result_update")
    return {"status": "ok"}
