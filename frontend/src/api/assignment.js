// src/apis/index.js

import instance from "."

/**
 * 获取课程作业列表的接口调用函数
 * @param {string} classUuid 课程 UUID，必填
 * @param {number} page 页码，默认1
 * @param {number} size 每页条数，默认10
 * @param {string} order_by 排序字段，默认 'created_at'
 * @param {string} order 排序方式，'asc' 或 'desc'，默认 'asc'
 * @param {string} status 筛选状态，可选，默认空字符串代表全部
 * @returns {Promise<{items: Array, pagination: Object}>} 返回作业数组和分页信息
 * @throws 请求失败时抛出异常
 */
export async function getAssignments(classUuid, page = 1, size = 10, order_by = 'created_at', order = 'asc', status = '') {
  try {

    // 组装请求 URL
    const url = `/api/v1/classes/${classUuid}/homeworks`

    // 构造请求参数对象
    const params = { page, size, order_by, order }
    if (status) {
      params.status = status
    }

    // 发送 GET 请求
    const res = await instance.get(url, { params })

    // 返回接口数据中真正需要的部分
    return {
      items: res.data.data.items,
      pagination: res.data.data.pagination,
    }
  } catch (error) {
    console.error('获取作业列表失败', error)
    throw error  // 让调用者可以捕获错误
  }
}
