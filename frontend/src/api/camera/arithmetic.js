import request from '@/utils/request'

//查询锂电池识别算法的运行状态
export function getLithiumBatteryStatus (query) {
  return request({
    url: '/battery/list',
    method: 'get',
    params: query
  })
}
//启动锂电池识别算法
export function startLithiumBattery () {
  return request({
    url: '/battery/start',
    method: 'get'
  })
}
//停止锂电池识别算法
export function stopLithiumBattery () {
  return request({
    url: '/battery/stop',
    method: 'get'
  })
}

//停止锂电池识别算法
export function changeLithiumBattery (data) {
  return request({
    url: '/battery/change',
    method: 'post',
    data
  })
}
