import request from '@/utils/request'
export function getStudentData() {
    return request({
      url: '/system/student/list',
      method: 'get'
    })
}
