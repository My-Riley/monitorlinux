import request from '@/utils/request'

// 查询摄像头预警列表（分页）
export function listWarn(query) {
    return request({
        url: '/camera/copy/list',
        method: 'get',
        params: query
    })
}
// 查询摄像头预警列表（不分页）
export function listWarnNo(query) {
    return request({
        url: '/camera/copy/list/no',
        method: 'get',
        params: query
    })
}
// 查询摄像头预警详细
export function getWarn(id) {
    return request({
        url: '/camera/copy/' + id,
        method: 'get'
    })
}

// 新增摄像头预警
export function addWarn(data) {
    return request({
        url: '/camera/warn',
        method: 'post',
        data: data
    })
}

// 修改摄像头预警
export function updateWarn(data) {
    return request({
        url: '/camera/warn',
        method: 'put',
        data: data
    })
}

// 删除摄像头预警
export function delWarn(id) {
    return request({
        url: '/camera/copy/' + id,
        method: 'delete'
    })
}

//通过摄像头Id对预警信息处理
export function handleWarn(id) {
    return request({
        url: '/camera/copy/warnHandleByCameraId/' + id,
        method: 'get',
    })
}
//通过Id对预警信息查看
export function getWarnById(ids) {
    return request({
        url: '/camera/copy/warnInformationByCameraId/' + ids,
        method: 'get',
    })
}
// 获取未处理的预警信息数量
export function getWarnCount() {
    return request({
        url: '/camera/warn/warnCount',
        method: 'get',
    })
}
