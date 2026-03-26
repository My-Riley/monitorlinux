import request from '@/utils/request'

// 查询电梯/摄像头列表
export function listCamera(query) {
  return request({
    url: '/camera/camera/list',
    method: 'get',
    params: query
  })
}

// 查询电梯/摄像头详细
export function getCamera(id) {
  return request({
    url: '/camera/camera/' + id,
    method: 'get'
  })
}

// 新增电梯/摄像头
export function addCamera(data) {
  return request({
    url: '/camera/camera',
    method: 'post',
    data: data
  })
}

// 修改电梯/摄像头
export function updateCamera(data) {
  return request({
    url: '/camera/camera',
    method: 'put',
    data: data
  })
}

// 删除电梯/摄像头
export function delCamera(id) {
  return request({
    url: '/camera/camera/' + id,
    method: 'delete'
  })
}

//根据区域id查询所属摄像头
export function getCameraByRegionId(id) {
  return request({
    url: '/camera/camera/list/' + id,
    method: 'get'
  })
}
export function algorithm(data) {
  return request({
    url: '/camera/camera/restart/algorithm',
    method: 'post',
    data
  })
}

// 查询摄像头是否在线
export function getCameraOnline(ip,port) {
  return request({
    url: '/hikvision/live/',
    method: 'get',
    params: {
      ip,
      port
    }
  })
}

export function importTemplate() {
  return request({
    url: '/camera/camera/importTemplate',
    method: 'get',
    responseType: 'blob',
  });
}
