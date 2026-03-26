/**
 * 通用js方法封装处理
 * Copyright (c) 2019 lanbu
 */

/* global $ */

// 日期格式化
export function parseTime(time, pattern) {
  if (arguments.length === 0 || !time) {
    return null
  }
  const format = pattern || '{y}-{m}-{d} {h}:{i}:{s}'
  let date
  if (typeof time === 'object') {
    date = time
  } else {
    if ((typeof time === 'string') && (/^[0-9]+$/.test(time))) {
      time = parseInt(time)
    } else if (typeof time === 'string') {
      time = time.replace(new RegExp(/-/gm), '/').replace('T', ' ').replace(new RegExp(/\.[\d]{3}/gm), '');
    }
    if ((typeof time === 'number') && (time.toString().length === 10)) {
      time = time * 1000
    }
    date = new Date(time)
  }
  const formatObj = {
    y: date.getFullYear(),
    m: date.getMonth() + 1,
    d: date.getDate(),
    h: date.getHours(),
    i: date.getMinutes(),
    s: date.getSeconds(),
    a: date.getDay()
  }
  const time_str = format.replace(/{(y|m|d|h|i|s|a)+}/g, (result, key) => {
    let value = formatObj[key]
    // Note: getDay() returns 0 on Sunday
    if (key === 'a') { return ['日', '一', '二', '三', '四', '五', '六'][value] }
    if (result.length > 0 && value < 10) {
      value = '0' + value
    }
    return value || 0
  })
  return time_str
}

// 表单重置
export function resetForm(refName) {
  if (this.$refs[refName]) {
    this.$refs[refName].resetFields();
  }
}

// 添加日期范围
export function addDateRange(params, dateRange, propName) {
  let search = params;
  search.params = typeof (search.params) === 'object' && search.params !== null && !Array.isArray(search.params) ? search.params : {};
  dateRange = Array.isArray(dateRange) ? dateRange : [];
  if (typeof (propName) === 'undefined') {
    search.params['beginTime'] = dateRange[0];
    search.params['endTime'] = dateRange[1];
  } else {
    search.params['begin' + propName] = dateRange[0];
    search.params['end' + propName] = dateRange[1];
  }
  return search;
}

// 回显数据字典
export function selectDictLabel(datas, value) {
  if (value === undefined) {
    return "";
  }
  var actions = [];
  Object.keys(datas).some((key) => {
    if (datas[key].value == ('' + value)) {
      actions.push(datas[key].label);
      return true;
    }
  })
  if (actions.length === 0) {
    actions.push(value);
  }
  return actions.join('');
}

// 回显数据字典（字符串、数组）
export function selectDictLabels(datas, value, separator) {
  if (value === undefined || value.length === 0) {
    return "";
  }
  if (Array.isArray(value)) {
    value = value.join(",");
  }
  var actions = [];
  var currentSeparator = undefined === separator ? "," : separator;
  var temp = value.split(currentSeparator);
  Object.keys(value.split(currentSeparator)).some((val) => {
    var match = false;
    Object.keys(datas).some((key) => {
      if (datas[key].value == ('' + temp[val])) {
        actions.push(datas[key].label + currentSeparator);
        match = true;
      }
    })
    if (!match) {
      actions.push(temp[val] + currentSeparator);
    }
  })
  return actions.join('').substring(0, actions.join('').length - 1);
}

// 字符串格式化(%s )
export function sprintf(str) {
  var args = arguments; var flag = true; var i = 1;
  str = str.replace(/%s/g, function () {
    var arg = args[i++];
    if (typeof arg === 'undefined') {
      flag = false;
      return '';
    }
    return arg;
  });
  return flag ? str : '';
}

// 转换字符串，undefined,null等转化为""
export function parseStrEmpty(str) {
  if (!str || str == "undefined" || str == "null") {
    return "";
  }
  return str;
}

// 数据合并
export function mergeRecursive(source, target) {
  for (var p in target) {
    try {
      if (target[p].constructor == Object) {
        source[p] = mergeRecursive(source[p], target[p]);
      } else {
        source[p] = target[p];
      }
    } catch (e) {
      source[p] = target[p];
    }
  }
  return source;
}

/**
 * 构造树型结构数据
 * @param {*} data 数据源
 * @param {*} id id字段 默认 'id'
 * @param {*} parentId 父节点字段 默认 'parentId'
 * @param {*} children 孩子节点字段 默认 'children'
 */
export function handleTree(data, id, parentId, children) {
  let config = {
    id: id || 'id',
    parentId: parentId || 'parentId',
    childrenList: children || 'children'
  };

  var childrenListMap = {};
  var nodeIds = {};
  var tree = [];

  for (let d of data) {
    let parentId = d[config.parentId];
    if (childrenListMap[parentId] == null) {
      childrenListMap[parentId] = [];
    }
    nodeIds[d[config.id]] = d;
    childrenListMap[parentId].push(d);
  }

  for (let d of data) {
    let parentId = d[config.parentId];
    if (nodeIds[parentId] == null) {
      tree.push(d);
    }
  }

  for (let t of tree) {
    adaptToChildrenList(t);
  }

  function adaptToChildrenList(o) {
    if (childrenListMap[o[config.id]] !== null) {
      o[config.childrenList] = childrenListMap[o[config.id]];
    }
    if (o[config.childrenList]) {
      for (let c of o[config.childrenList]) {
        adaptToChildrenList(c);
      }
    }
  }
  return tree;
}

/**
* 参数处理
* @param {*} params  参数
*/
export function tansParams(params) {
  let result = ''
  for (const propName of Object.keys(params)) {
    const value = params[propName];
    var part = encodeURIComponent(propName) + "=";
    if (value !== null && value !== "" && typeof (value) !== "undefined") {
      if (typeof value === 'object') {
        for (const key of Object.keys(value)) {
          if (value[key] !== null && value[key] !== "" && typeof (value[key]) !== 'undefined') {
            let params = propName + '[' + key + ']';
            var subPart = encodeURIComponent(params) + "=";
            result += subPart + encodeURIComponent(value[key]) + "&";
          }
        }
      } else {
        result += part + encodeURIComponent(value) + "&";
      }
    }
  }
  return result
}

// 验证是否为blob格式
export function blobValidate(data) {
  return data.type !== 'application/json'
}

export function WebVideo() {
  this.g_iWndIndex = 0
  this.szDeviceIdentify = ''
  this.deviceport = ''
  this.rtspPort = ''
  this.channels = []
  this.ip = ''
  this.port = '80'
  this.username = ''
  this.password = ''
  this.crmeraId = ''
  this.init = function (ip, username, password, crmeraId) {
    this.ip = ip
    this.username = username
    this.password = password
    // var self = this
    // 检查插件是否已经安装过
    // var iRet = webVideoCtrl.I_CheckPluginInstall();
    // if (-1 == iRet) {
    //     alert("您还未安装过插件，双击开发包目录里的WebComponentsKit.exe安装！");
    //     return;
    // }
    // 初始化插件参数及插入插件
    window.WebVideoCtrl.I_InitPlugin({
      szColorProperty: 'plugin-background:#102749; sub-background:#102749; sub-border:#18293c; sub-border-select:red',
      bWndFull: true, // 全屏
      // iPackageType: 2,
      iWndowType: 1, //分屏
      // bNoPlugin: true, // 支持无插件
      cbInitPluginComplete: function () {
        window.WebVideoCtrl.I_InsertOBJECTPlugin(crmeraId);
      }
    });
  }
  // 登录
  this.clickLogin = function () {
    var self = this
    if (self.ip == "" || self.port == "") {
      return;
    }
    self.szDeviceIdentify = self.ip + "_" + self.port;

    window.WebVideoCtrl.I_Login(self.ip, 1, self.port, self.username, self.password, {
      success: function (xmlDoc) {
        setTimeout(function () {
          self.getChannelInfo();
          self.getDevicePort();
        }, 10);
        setTimeout(function () {
          self.clickStartRealPlay()
        }, 500)
      },
      error: function (status, xmlDoc) {
      }
    });
  }
  // 退出
  this.clickLogout = function () {
    var self = this
    self.channels = []

    if (self.szDeviceIdentify == null) {
      return;
    }
    var iRet = window.WebVideoCtrl.I_Logout(self.szDeviceIdentify);
    if (iRet == 0) {
      self.getChannelInfo();
      self.getDevicePort();
    }
  }
  // 获取通道
  this.getChannelInfo = function () {
    var self = this
    self.channels = []
    if (self.szDeviceIdentify == null) {
      return;
    }
    // 模拟通道
    window.WebVideoCtrl.I_GetAnalogChannelInfo(self.szDeviceIdentify, {
      async: false,
      success: function (xmlDoc) {
        var oChannels = $(xmlDoc).find("VideoInputChannel");
        $.each(oChannels, function (i) {
          var id = $(this).find("id").eq(0).text();
          var name = $(this).find("name").eq(0).text();
          if (name == "") {
            name = "Camera " + (i < 9 ? "0" + (i + 1) : (i + 1));
          }
          self.channels.push({
            id: id,
            name: name
          })
        });
      },
      error: function (status, xmlDoc) {
      }
    });
  }
  // 获取端口
  this.getDevicePort = function () {
    var self = this
    if (self.szDeviceIdentify == null) {
      return;
    }
    var oPort = window.WebVideoCtrl.I_GetDevicePort(self.szDeviceIdentify);
    if (oPort != null) {
      self.deviceport = oPort.iDevicePort;
      self.rtspPort = oPort.iRtspPort;
    }
  }

  // 开始预览
  this.clickStartRealPlay = function () {
    var self = this
    var oWndInfo = window.WebVideoCtrl.I_GetWindowStatus(self.g_iWndIndex);
    var iChannelID = self.channels[0].id

    if (self.szDeviceIdentify == null) {
      return;
    }
    var startRealPlay = function () {
      window.WebVideoCtrl.I_StartRealPlay(self.szDeviceIdentify, {
        iChannelID: iChannelID,
        bZeroChannel: false,
        iStreamType: 2,
        success: function () {
        },
        error: function (status, xmlDoc) {
          if (status === 403) {
          } else {
          }
        }
      });
    };

    if (oWndInfo != null) { // 已经在播放了，先停止
      window.WebVideoCtrl.I_Stop({
        success: function () {
          startRealPlay();
        }
      });
    } else {
      startRealPlay();
    }
  }
  // 停止预览
  this.clickStopRealPlay = function () {
    var self = this
    var oWndInfo = window.WebVideoCtrl.I_GetWindowStatus(self.g_iWndIndex)
    if (oWndInfo != null) {
      window.WebVideoCtrl.I_Stop({
        success: function () {
        },
        error: function () {
        }
      });
    }
  }
}
