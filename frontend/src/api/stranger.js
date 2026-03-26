import request from '@/utils/request'

// 陌生人员信息获取
export const getStrangerInfo = (data) => {
    return request({
        url: "/system/results/listUnknown",
        method: "GET",
        params: data
    })
}
