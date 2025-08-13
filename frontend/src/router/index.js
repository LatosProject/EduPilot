// src/router/index.js

// 从 Vue Router 导入创建路由的方法

import { createRouter, createWebHashHistory } from 'vue-router'

import HomePage from '../views/HomePage.vue'
import LoginPage from '../views/LoginPage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import StudyPage from '../views/StudyPage.vue'
import { authGuard } from './guards'
import { getAssignments } from '../api/assignment'
import { useGlobalStore } from '../stores/global'

// 导入自定义路由守卫（authGuard 用来做登录权限校验）


// 路由表
const routes = [
  // 首页（需要登录权限）
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true } // 自定义 meta 标记，表示此路由需要身份验证
  },

  // 登录页（不需要登录即可访问）
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },

  // 作业详情页（当前使用 HomePage 组件作为占位）
  {
    path: '/assignment/:id', // 动态路由，:id 为作业 ID
    name: 'AssignmentDetail',
    component: HomePage,
    meta: { requiresAuth: true }
  },

  // 设置页
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true }
  },

  // 学习页面
  {
    path: '/study',
    name: 'Study',
    component: StudyPage,
    meta: { requiresAuth: true }
  },
  // 路由示例
  {
    path: '/login/username',
    component: LoginPage,
  },
  {
    path: '/login/password',
    component: LoginPage,
  },
]

// 创建路由实例
const router = createRouter({
  history: createWebHashHistory(), // 改为 hash 模式
  routes
})

// 全局前置守卫
// 每次路由跳转前都会执行 authGuard（用来检查用户是否已登录）
router.beforeEach(authGuard)


router.beforeResolve(async (to, from, next) => {
  const globalStore = useGlobalStore()
  // 如果没登录或不需要认证的页面，直接放行
  if (!to.meta.requiresAuth || !globalStore.classUuid || to.path === '/') {
    return next()
  }
  const res = await getAssignments(globalStore.classUuid, 1, 10, 'created_at', 'asc', 'pending')
  globalStore.setBadgeCount(res.pagination.total)
  next()
})
// 导出路由实例，供 main.js 挂载到应用
export default router
