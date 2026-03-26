import request from '@/utils/request'

// 查询课程列表
export function listCourse(query) {
  return request({
    url: '/cell/course/list',
    method: 'get',
    params: query
  })
}

export function listCourseClasses() {
  return request({
    url: '/cell/course/classes',
    method: 'get'
  })
}

export function listCourseSubjects() {
  return request({
    url: '/cell/course/subjects',
    method: 'get'
  })
}

export function listCourseWeeks(semesterId) {
  return request({
    url: '/cell/course/weeks',
    method: 'get',
    params: { semesterId }
  })
}

// 查询课程详细
export function getCourse(courseId) {
  return request({
    url: '/cell/course/' + courseId,
    method: 'get'
  })
}

// 新增课程
export function addCourse(data) {
  return request({
    url: '/cell/course',
    method: 'post',
    data: data
  })
}

// 修改课程
export function updateCourse(data) {
  return request({
    url: '/cell/course',
    method: 'put',
    data: data
  })
}

// 删除课程
export function delCourse(courseId) {
  return request({
    url: '/cell/course/' + courseId,
    method: 'delete'
  })
}

export function listSemesters() {
  return request({
    url: '/cell/semester/list',
    method: 'get'
  })
}

export function addSemester(data) {
  return request({
    url: '/cell/semester',
    method: 'post',
    data
  })
}

export function updateSemester(data) {
  return request({
    url: '/cell/semester',
    method: 'put',
    data
  })
}

export function delSemester(semesterId) {
  return request({
    url: '/cell/semester/' + semesterId,
    method: 'delete'
  })
}

export function listCycles(semesterId) {
  return request({
    url: '/cell/semester/cycles',
    method: 'get',
    params: { semesterId }
  })
}

export function listSemesterWeeks(semesterId) {
  return request({
    url: '/cell/semester/weeks',
    method: 'get',
    params: { semesterId }
  })
}

export function addCycle(data) {
  return request({
    url: '/cell/semester/cycle',
    method: 'post',
    data
  })
}

export function updateCycle(data) {
  return request({
    url: '/cell/semester/cycle',
    method: 'put',
    data
  })
}

export function delCycle(cycleId) {
  return request({
    url: '/cell/semester/cycle/' + cycleId,
    method: 'delete'
  })
}

export function importCourseTemplate() {
  return request({
    url: '/cell/course/importTemplate',
    method: 'get',
    responseType: 'blob'
  })
}
