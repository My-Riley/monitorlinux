import request from '@/utils/request'

// 查询区域列表
export function listRegion(query) {
  return request({
    url: '/camera/region/list',
    method: 'get',
    params: query
  })
}

// 查询区域树结构
export function treeRegion() {
  return request({
    url: '/camera/region/tree',
    method: 'get'
  })
}

// 查询区域详细
export function getRegion(regionId) {
  return request({
    url: '/camera/region/' + regionId,
    method: 'get'
  })
}

// 新增区域
export function addRegion(data) {
  return request({
    url: '/camera/region',
    method: 'post',
    data: data
  })
}

// 修改区域
export function updateRegion(data) {
  return request({
    url: '/camera/region',
    method: 'put',
    data: data
  })
}

// 删除区域
export function delRegion(regionId) {
  return request({
    url: '/camera/region/' + regionId,
    method: 'delete'
  })
}
