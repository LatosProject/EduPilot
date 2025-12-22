// src/apis/index.js

import axios from "axios";
import { refreshToken } from "./auth";
import router from '@/router';

// 创建 Axios 实例
const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 5000,
  withCredentials: true,
});

// 请求拦截器：注入 token
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// --- 响应拦截器设置刷新机制 ---
const MAX_RETRY_ATTEMPTS = 3;    // 最大重试次数
const REFRESH_RETRY_DELAY = 100; // 每次重试延迟(ms)

let isRefreshing = false;        // 是否正在刷新 token
let refreshSubscribers = [];     // 刷新队列

/**
 * 添加回调到刷新队列
 * @param {Function} cb 回调函数
 */
function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

/**
 * token 刷新完成后通知队列中的请求
 * @param {String} token 新 token
 */
function onRefreshed(token) {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
}

/**
 * 延迟函数
 * @param {Number} ms 毫秒
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

instance.interceptors.response.use(
  response => response,

  async (error) => {
    const originalRequest = error.config;

    // 401 未授权处理
    if (error.response && error.response.status === 401) {

      // 正在刷新，加入队列等待
      if (isRefreshing) {
        return new Promise(resolve => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            resolve(instance(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        for (let attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt++) {
          try {
            await refreshToken();
            const newToken = localStorage.getItem('access_token');

            // 通知等待队列
            onRefreshed(newToken);

            // 重试原请求
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return instance(originalRequest);
          } catch (err) {
            console.error(`刷新失败，第${attempt}次，等待${REFRESH_RETRY_DELAY}ms`, err);
            await sleep(REFRESH_RETRY_DELAY);
          }
        }

        // 多次刷新失败，清理并跳转登录
        console.error('刷新 token 多次失败，跳转登录');
        localStorage.removeItem('access_token');
        await router.replace({ name: 'Login' });
        return Promise.reject(error);

      } finally {
        isRefreshing = false; // 确保状态恢复
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
