// src/apis/index.js

import axios from 'axios'
import { refreshToken } from './auth'

const instance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
  withCredentials: true,
})

instance.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

instance.interceptors.response.use(
  response => response,
  async error => {
    if (error.response) {
      const status = error.response.status
      if (status === 401) {
        try {
          refreshToken()
          const newToken = localStorage.getItem('access_token')
          error.config.headers.Authorization = `Bearer ${newToken}`
          return instance(error.config)
        } catch (err) {
          //彻底重置应用状态（有时在拦截器里用 router.push，
          //页面跳转后 axios 可能还在继续执行，容易造成状态不一致或重复跳转）
          window.location.href = '/login'
          return Promise.reject(err)
        }
      }
    }
    return Promise.reject(error)
  }
)
export default instance
