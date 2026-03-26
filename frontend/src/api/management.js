import request from "@/utils/request";

//查询情绪数量Echarts数据
export function getEmotionCount(query) {
  return request({
    url: "/system/results/listUserChart",
    method: "get",
    params: query,
  });
}
//查询情绪地点Echarts数据
export function getEmotionPlace(query) {
  return request({
    url: "/system/results/listAddressChart",
    method: "get",
    params: query,
  });
}
