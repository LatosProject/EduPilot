// src/router/index.js

// 从 Vue Router 导入创建路由的方法

import { createRouter, createWebHashHistory } from 'vue-router'

import HomePage from '../views/HomePage.vue'
import InvitePage from '../views/InvitePage.vue'
import LoginPage from '../views/LoginPage.vue'
import SettingsPage from '../views/SettingsPage.vue'
import StudyPage from '../views/StudyPage.vue'
import { authGuard } from './guards'
import { getAssignments } from '../api/assignment'
import { useGlobalStore } from '../stores/global'

// 路由表
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true } 
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/assignment/:id', 
    name: 'AssignmentDetail',
    component: HomePage,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/study',
    name: 'Study',
    component: StudyPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/login/username',
    component: LoginPage,
  },
  {
    path: '/login/password',
    component: LoginPage,
  },
    {
    name: 'Invite',
    path: '/invite',
    component: InvitePage,
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
  if (!to.meta.requiresAuth || !globalStore.classUuids.length || to.path === '/') {
    return next()
  }

  try {
    let totalBadge = 0
    for (const cls of globalStore.classUuids) {
      const res = await getAssignments(cls, 1, 10, 'created_at', 'asc', 'pending')
      totalBadge += res.pagination?.total || 0
    }
    globalStore.setBadgeCount(totalBadge)
  } catch (e) {
    console.error('刷新徽章失败', e)
  }

  next()
})
// 导出路由实例，供 main.js 挂载到应用
export default router
