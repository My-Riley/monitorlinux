import request from '@/utils/request'
import { parseStrEmpty } from "@/utils/lanbu";

// 查询管理员用户列表
export function listAdmin(query) {
    return request({
        url: '/system/admin/list',
        method: 'get',
        params: query
    })
}

// 查询管理员用户详细
export function getAdmin(userId) {
    return request({
        url: '/system/admin/' + parseStrEmpty(userId),
        method: 'get'
    })
}

// 新增管理员用户
export function addAdmin(data) {
    return request({
        url: '/system/admin',
        method: 'post',
        data: data
    })
}

// 修改管理员用户
export function updateAdmin(data) {
    return request({
        url: '/system/admin',
        method: 'put',
        data: data
    })
}

// 删除管理员用户
export function delAdmin(userId) {
    return request({
        url: '/system/admin/' + userId,
        method: 'delete'
    })
}

// 用户密码重置
export function resetAdminPwd(userId, password) {
    const data = {
        userId,
        password
    }
    return request({
        url: '/system/admin/resetPwd',
        method: 'put',
        data: data
    })
}

// 用户状态修改
export function changeAdminStatus(userId, status) {
    const data = {
        userId,
        status
    }
    return request({
        url: '/system/admin/changeStatus',
        method: 'put',
        data: data
    })
}

// 查询部门下拉树结构
export function deptTreeSelect() {
    return request({
        url: '/system/dept/treeselect',
        method: 'get'
    })
}

// 导出管理员用户
export function exportAdmin(query) {
    return request({
        url: '/system/admin/export',
        method: 'get',
        params: query
    })
}
