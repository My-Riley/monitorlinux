// 定义配置对象
const config = {
  serverIP: "http://localhost:9099",
  wsIP: "ws://localhost:9099/ws",
  pythonIP: "localhost:5001",
};

// 浏览器环境下挂载到window
if (typeof window !== 'undefined') {
  window.config = config;
}

// Node.js环境下导出模块
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
  module.exports = config;
  module.exports.pythonIP = config.pythonIP;
};
