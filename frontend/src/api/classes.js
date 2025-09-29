import request from './index'

export async function getClass(page = 1, size = 25, search = undefined) {
    const params = { page, size, search }
    const res = await request.get('/api/v1/classes', { params })
    return {
        items: res.data.data.items,
        pagination: res.data.data.pagination,
    }
}

export function joinClass(inviteCode) {
  return request.post('/api/v1/classes/students', { invite_code: inviteCode })
}