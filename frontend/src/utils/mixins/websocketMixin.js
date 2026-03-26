export default {
  data() {
    return {
      ws: null,
      wsConnected: false,
      wsHeartbeatInterval: 30000,
      wsHeartbeatTimer: null,
    };
  },
  mounted() {
    this.initWebSocket();
  },
  beforeDestroy() {
    this.closeWebSocket();
  },
  methods: {
    initWebSocket() {
      if (typeof WebSocket === "undefined") {
        console.error("您的浏览器不支持WebSocket");
        return;
      }

      // 生成随机客户端ID
      const clientId = Math.random().toString(36).substring(7);
      
      // 获取WebSocket地址，优先使用全局配置，并支持动态 hostname
      let wsUrl = window.config?.wsIP;
      
      if (!wsUrl || wsUrl.includes("localhost")) {
        // 如果配置为空或包含 localhost，尝试使用当前页面的 hostname 动态构建
        const hostname = window.location.hostname;
        const port = window.config?.serverIP ? window.config.serverIP.split(':').pop() : '9099';
        // 确保使用 ws 协议
        wsUrl = `ws://${hostname}:${port}/ws`;
      }
      
      // 移除末尾斜杠
      if (wsUrl.endsWith('/')) {
        wsUrl = wsUrl.slice(0, -1);
      }
      wsUrl = `${wsUrl}/${clientId}`;
      
      try {
        this.ws = new WebSocket(wsUrl);
        this.ws.onopen = this.onWsOpen;
        this.ws.onmessage = this.onWsMessage;
        this.ws.onerror = this.onWsError;
        this.ws.onclose = this.onWsClose;
      } catch (e) {
        console.error("WebSocket连接创建失败:", e);
      }
    },
    onWsOpen() {
      this.wsConnected = true;
      this.startHeartbeat();
    },
    onWsMessage(event) {
      const message = event.data;
      
      if (message === "result_update") {
        // 优先调用组件定义的更新处理方法
        if (this.handleWebSocketUpdate) {
          this.handleWebSocketUpdate();
        } else {
          // 默认尝试刷新列表或查询
          if (this.getList) {
            this.getList();
          } else if (this.handleQuery) {
            // 对于首页 index.vue，handleQuery 可能需要参数
            // 这里不做通用处理，由组件自己实现 handleWebSocketUpdate 更好
            // 但为了兼容简单情况，如果 handleQuery 不需要参数或组件处理了...
            // 实际上 index.vue 的 handleQuery 需要 type 参数。
            // 所以 index.vue 必须实现 handleWebSocketUpdate。
          }
        }
      } else if (message === "pong") {
        // 心跳响应，忽略
      }
    },
    onWsError(error) {
      console.error("WebSocket错误:", error);
    },
    onWsClose() {
      this.wsConnected = false;
      this.stopHeartbeat();
    },
    startHeartbeat() {
      this.stopHeartbeat();
      this.wsHeartbeatTimer = setInterval(() => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          this.ws.send("ping");
        }
      }, this.wsHeartbeatInterval);
    },
    stopHeartbeat() {
      if (this.wsHeartbeatTimer) {
        clearInterval(this.wsHeartbeatTimer);
        this.wsHeartbeatTimer = null;
      }
    },
    closeWebSocket() {
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
    }
  }
};
