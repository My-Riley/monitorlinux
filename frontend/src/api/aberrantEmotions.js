import request from "@/utils/request";

// 查询情绪情列表
export function listResults(query) {
  return request({
    url: "/system/results/list",
    method: "get",
    params: query,
  });
}

// 查询重点关注人与
export function listFocus(query) {
  return request({
    url: "/system/results/listFocus",
    method: "get",
    params: query,
  });
}

// 查询情绪情详细
export function getResults(id) {
  return request({
    url: "/system/results/" + id,
    method: "get",
  });
}

// 新增情绪情
export function addResults(data) {
  return request({
    url: "/system/results",
    method: "post",
    data: data,
  });
}

// 修改情绪情
export function updateResults(data) {
  return request({
    url: "/system/results",
    method: "put",
    data: data,
  });
}

// 删除情绪情
export function delResults(id) {
  return request({
    url: "/system/results/" + id,
    method: "delete",
  });
}

// 导出情绪识别结果
export function exportResults(query) {
  return request({
    url: "/system/results/export",
    method: "get",
    params: query,
    responseType: "blob",
  });
}

//用户信息
export function getUserInfo() {
  return request({
    url: "/system/results/listUser",
    method: "get",
  });
}
