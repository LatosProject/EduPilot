import request from './index'

/**
 * 获取班级列表
 * @param {Number} page 页码，默认 1
 * @param {Number} size 每页数量，默认 25
 * @param {String|undefined} search 搜索关键字，可选
 * @returns {Promise<{items: Array, pagination: Object}>} 返回班级列表和分页信息
 */
export async function getClass(page = 1, size = 25, search = undefined) {
    const params = { page, size, search }
    const res = await request.get('/api/v1/classes', { params })
    return {
        items: res.data.data.items,
        pagination: res.data.data.pagination,
    }
}

/**
 * 使用邀请码加入班级
 * @param {String} inviteCode 班级邀请码
 * @returns {Promise} 返回请求结果
 */
export function joinClass(inviteCode) {
    return request.post('/api/v1/classes/students', { invite_code: inviteCode })
}
