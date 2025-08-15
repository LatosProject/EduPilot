import request from './index'

export async function getClass(page = 1, size = 25, search = undefined) {
    const params = { page, size, search }
    const res = await request.get('/api/v1/classes', { params })
    return {
        items: res.data.data.items,
        pagination: res.data.data.pagination,
    }
}