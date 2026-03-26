import request from "@/utils/request";

// 查询该部门下的今日报警数量
export function getWarnCount() {
  return request({
    url: "/camera/warn/query/department/warn",
    method: "get",
  });
}
//最近30天锂电池和电瓶车的报警数量
export function getBatteryWarnCount() {
  return request({
    url: "/camera/warn/query/department/thirty",
    method: "get",
  });
}
//查询该部门下的所有报警数量
export function getAllWarnCount() {
  return request({
    url: "/camera/warn/query/department/count",
    method: "get",
  });
}

//查询首页数据
export function getHomeData() {
  return request({
    url: "/system/results/listUser",
    method: "get",
  });
}
export function getOverallTrend(params) {
  return request({
    url: '/system/results/dashboard/overall',
    method: 'get',
    params
  });
}
