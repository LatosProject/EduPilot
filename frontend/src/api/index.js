// src/apis/index.js

import axios from "axios";
import { refreshToken } from "./auth";
import router from '@/router'

const instance = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 5000,
  withCredentials: true,
});

instance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


const MAX_RETRY_ATTEMPTS = 3;
const REFRESH_RETRY_DELAY = 300;

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token) {
  refreshSubscribers.forEach(cb => cb(token));
  refreshSubscribers = [];
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

instance.interceptors.response.use(
  (response) => response,

  async (error) => {
    if (error.response && error.response.status === 401) {
      const originalRequest = error.config;

      // 如果正在刷新，则排队
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

            onRefreshed(newToken);
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return instance(originalRequest);
          } catch (err) {
            console.error(`刷新失败，第${attempt}次，等待${REFRESH_RETRY_DELAY}ms`, err);
            await sleep(REFRESH_RETRY_DELAY);
          }
        }

        // 三次都失败
        console.error('刷新 token 多次失败，跳转登录');
        localStorage.removeItem('access_token');
        await router.replace({'name':'Login'});
        return Promise.reject(error);

      } finally {
        isRefreshing = false;   // 确保状态恢复
      }
    }

    return Promise.reject(error);
  }
);

export default instance;
