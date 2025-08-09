// api/auth.js
import request from './index'  // axios 实例，统一配置请求基础路径、拦截器等

// 登录接口，传入用户名和密码，返回 Promise
export function login(username, password) {
  return request.post('/api/v1/auth/login', { username, password })
}

// 获取本地存储的 access_token
export function getAccessToken() {
  return localStorage.getItem('access_token')
}

// 获取当前用户信息
export function getProfile() {
  return request.get('/api/v1/auth/profile')
}

// 刷新 token，调用后端刷新接口，返回新的 access_token 和过期时间
export async function refreshToken() {
  const response = await request.post('/api/v1/auth/refresh', {}, { withCredentials: true })
  const { access_token, expires_in } = response.data.data
  localStorage.setItem('access_token', access_token)
  return { access_token, expires_in }
}

// 验证 token 是否有效
export async function verifyToken() {
  try {
    const response = await request.get('/api/v1/auth/verify_token')
    return {
      status: response.data.status,
      message: response.data.message
    }
  } catch (error) {
    const backendResponse = error.response

    if (backendResponse && backendResponse.data) {
      return {
        status: backendResponse.data.status,
        message: backendResponse.data.message
      }
    }

    // 网络错误或无响应时，返回默认失败状态
    return {
      status: -1,
      message: '网络或服务器错误'
    }
  }
}
