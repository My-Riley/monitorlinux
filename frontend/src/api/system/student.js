// api/system/student.js
import request from '@/utils/request';

// 查询学生列表
export function listStudent(query) {
  return request({
    url: '/system/student/list',
    method: 'get',
    params: query
  });
}

// 获取班级下拉选项
export function getClassList() {
  return request({
    url: '/system/student/classes',
    method: 'get'
  });
}

// 根据姓名关键词搜索（用于 autocomplete）
export function searchStudents(keyword) {
  return request({
    url: '/system/student/search',
    method: 'get',
    params: { keyword }
  });
}

// 根据学号关键词搜索（用于 autocomplete）
export function searchStudentIds(keyword) {
  return request({
    url: '/system/student/search',
    method: 'get',
    params: { keyword, type: 'studentId' }
  });
}

// 获取学生详情（用于编辑）
export function getStudent(id) {
  return request({
    url: '/system/student/' + id,
    method: 'get'
  });
}

// 新增学生
export function addStudent(data) {
  return request({
    url: '/system/student',
    method: 'post',
    data: data
  });
}

// 修改学生
export function updateStudent(data) {
  return request({
    url: '/system/student',
    method: 'put',
    data: data
  });
}

// 删除学生（支持批量）
export function delStudent(studentIds) {
  return request({
    url: '/system/student/' + studentIds,
    method: 'delete'
  });
}

// 导出学生
export function exportStudent(query) {
  return request({
    url: '/system/student/export',
    method: 'get',
    params: query,
    responseType: 'blob'
  });
}

// 下载导入模板
export function importTemplate() {
  return request({
    url: '/system/student/importTemplate',
    method: 'get',
    responseType: 'blob'
  });
}
