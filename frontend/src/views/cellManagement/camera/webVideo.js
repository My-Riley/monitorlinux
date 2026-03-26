// 初始化插件
// import WebVideoCtrl from './webVideoCtrl1.js'
// import jsVideoPlugin from './jsVideoPlugin-1.0.0.min.js'
import $ from "jquery";
export function WebVideo() {
  // var $ = require('jquery');

  require("./webVideoCtrl1.js");
  require("./jsVideoPlugin-1.0.0.min.js");
  require("./jsPlugin-1.2.0.min");
  this.g_iWndIndex = 0;
  this.szDeviceIdentify = "";
  this.deviceport = "";
  this.rtspPort = "";
  this.channels = [];
  this.ip = "";
  this.port = "80";
  this.username = "";
  this.password = "";
  // this.init = function (ip, username, password, CameraId) {
  this.init = function (CameraId) {
    // this.ip = ip
    // this.username = username
    // this.password = password
    // var self = this
    // 检查插件是否已经安装过
    // var iRet = webVideoCtrl.I_CheckPluginInstall();
    // if (-1 == iRet) {
    //     alert("您还未安装过插件，双击开发包目录里的WebComponentsKit.exe安装！");
    //     return;
    // }云南。 ****真的我知道了我知道了你看。
    // 初始化插件参数及插入插件
    window.WebVideoCtrl.I_InitPlugin({
      szColorProperty:
        "plugin-background:#102749; sub-background:#102749; sub-border:#18293c; sub-border-select:red",
      bWndFull: true, // 全屏
      // iPackageType: 2,
      iWndowType: 1, //分屏
      bNoPlugin: true, // 支持无插件
      cbInitPluginComplete: function () {
        window.WebVideoCtrl.I_InsertOBJECTPlugin(CameraId);
      },
    });
  };
  this.close_JSVideoPlugin = function () {
    window.WebVideoCtrl.I_DestroyPlugin().then(
      (res) => {
      },
      () => {
      }
    );
  };

  // 登录
  this.clickLogin = function (ip, username, password, index) {
    var self = this;
    if (ip == "" || self.port == "") {
      return;
    }

    let szDeviceIdentify = ip + "_" + self.port;
    // self.szDeviceIdentify = ip + "_" + self.port;

    window.WebVideoCtrl.I_Login(ip, 1, self.port, username, password, {
      success: function (xmlDoc) {
        setTimeout(function () {
          self.getChannelInfo(szDeviceIdentify);
          self.getDevicePort(szDeviceIdentify);
        }, 10);
        setTimeout(function () {
          self.clickStartRealPlay(szDeviceIdentify, index);
          // self.clickOpenSound()
          // self.StartAudioPlay()
        }, 500);
      },
      error: function (status, xmlDoc) {},
    });
  };
  // 退出
  this.clickLogout = function (ip) {
    var self = this;
    self.channels = [];
    let szDeviceIdentify = ip + "_" + self.port;
    if (szDeviceIdentify == null) {
      return;
    }
    // var iRet = window.WebVideoCtrl.I_Logout(szDeviceIdentify);
    // if (0 == iRet) {
    //     self.getChannelInfo();
    //     self.getDevicePort();
    // }
    I_Logout(szDeviceIdentify).then(
      () => {},
      () => {}
    );
  };
  // 打开声音
  this.clickOpenSound = function () {
    var oWndInfo = window.WebVideoCtrl.I_GetWindowStatus(self.g_iWndIndex);
      var szInfo = "";
    if (oWndInfo != null) {
      var allWndInfo = window.WebVideoCtrl.I_GetWindowStatus();
      //   循环遍历所有窗口，如果有窗口打开了声音，先关闭
      for (var i = 0, iLen = allWndInfo.length; i < iLen; i++) {
        oWndInfo = allWndInfo[i];
        if (oWndInfo.bSound) {
          window.WebVideoCtrl.I_CloseSound(oWndInfo.iIndex);
          break;
        }
      }
      window.WebVideoCtrl.I_OpenSound().then(
        () => {
        },
        (oError) => {
        }
      );
    }
  };
  // 获取通道
  this.getChannelInfo = function (szDeviceIdentify) {
    var self = this;
    self.channels = [];
    if (szDeviceIdentify == null) {
      return;
    }
    // 模拟通道
    window.WebVideoCtrl.I_GetAnalogChannelInfo(szDeviceIdentify, {
      async: false,
      success: function (xmlDoc) {
        var oChannels = $(xmlDoc).find("VideoInputChannel");
        $.each(oChannels, function (i) {
          var id = $(this).find("id").eq(0).text();
            var name = $(this).find("name").eq(0).text();
          if (name == "") {
            name = "Camera " + (i < 9 ? "0" + (i + 1) : i + 1);
          }
          self.channels.push({
            id: id,
            name: name,
          });
        });
      },
      error: function (status, xmlDoc) {
      },
    });
  };
  // 获取端口
  this.getDevicePort = function (szDeviceIdentify) {
    var self = this;
    if (szDeviceIdentify == null) {
      return;
    }
    var oPort = window.WebVideoCtrl.I_GetDevicePort(szDeviceIdentify);
    if (oPort != null) {
      self.deviceport = oPort.iDevicePort;
      self.rtspPort = oPort.iRtspPort;
    }
  };
  this.StartAudioPlay = function () {
    var self = this;
    window.WebVideoCtrl.I_StartAudioPlay(szDeviceIdentify, {
      iAudioType: 1,
      szUrl: "./gcl.wav",
    }).then(
      (res) => {
      },
      () => {}
    );
  };
  // 开始预览
  this.clickStartRealPlay = function (szDeviceIdentify, index) {
    var self = this;
    var oWndInfo = window.WebVideoCtrl.I_GetWindowStatus(index);
      var iChannelID = self.channels[0].id;
    if (szDeviceIdentify == null) {
      return;
    }

    var startRealPlay = function () {
      window.WebVideoCtrl.I_StartRealPlay(szDeviceIdentify, {
        iWndIndex: index,
        iChannelID: iChannelID,
        bZeroChannel: false,
        iStreamType: 2,
        success: function () {
          // console.log('预览成功')
        },
        error: function (status, xmlDoc) {
          if (status === 403) {
          } else {
          }
        },
      });
    };

    if (oWndInfo != null) {
      // 已经在播放了，先停止
      window.WebVideoCtrl.I_Stop({
        success: function () {
          startRealPlay();
        },
      });
    } else {
      startRealPlay();
    }
  };
  // 停止预览
  this.clickStopRealPlay = function (index) {
    var self = this;
    var oWndInfo = window.WebVideoCtrl.I_GetWindowStatus(index);
    if (oWndInfo != null) {
      window.WebVideoCtrl.I_Stop({
        success: function () {
        },
        error: function () {
        },
      });
    }
  };
}
