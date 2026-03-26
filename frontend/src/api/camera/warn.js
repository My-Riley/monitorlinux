import request from '@/utils/request'

// 查询预警列表
export function listWarn(query) {
  return request({
    url: '/camera/warn/list',
    method: 'get',
    params: query
  })
}

// 查询预警详细
export function getWarnById(warnId) {
  return request({
    url: '/camera/warn/' + warnId,
    method: 'get'
  })
}

// 兼容旧的 getWarn
export function getWarn(warnId) {
  return getWarnById(warnId)
}

// 查询未处理的预警列表 (自定义接口)
export function listWarnNo(params) {
  return request({
    url: '/camera/warn/list', // 暂时复用 list 接口，如果后端有专用接口需修改
    method: 'get',
    params: params
  })
}

// 获取预警数量
export function getWarnCount() {
  return request({
    url: '/camera/warn/count', // 假设后端有这个接口，或者复用 list 并取 total
    method: 'get'
  })
}

// 处理预警
export function handleWarn(data) {
    return request({
      url: '/camera/warn/handle',
      method: 'put',
      data: data
    })
  }

// 新增预警
export function addWarn(data) {
  return request({
    url: '/camera/warn',
    method: 'post',
    data: data
  })
}

// 修改预警
export function updateWarn(data) {
  return request({
    url: '/camera/warn',
    method: 'put',
    data: data
  })
}

// 删除预警
export function delWarn(warnId) {
  return request({
    url: '/camera/warn/' + warnId,
    method: 'delete'
  })
}
