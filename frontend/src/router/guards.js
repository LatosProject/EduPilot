// src/router/guards.js

// 从认证服务中导入相关方法和常量
import {
    getAccessToken,     // 从 localStorage 获取 access_token
    verifyToken,       // 调用后端接口验证 token 是否有效
    refreshToken, // 调用后端刷新 token
} from '../api/auth'

// 跳转到登录页的辅助函数
function goLogin(next) {
    return next({ name: 'Login' })
}

// 跳转到首页的辅助函数
function goHome(next) {
    return next({ name: 'Home' })
}

/**
 * 全局路由守卫（authGuard）
 * 每次路由跳转前执行，用于校验用户是否登录和 token 是否有效
 */
export async function authGuard(to, from, next) {
    const token = getAccessToken()

    // 无 token 需要权限页面，且不是登录页才跳登录页
    if (!token && to.meta.requiresAuth && to.name !== 'Login') return goLogin(next)

    if (!token) return next()

    const result = await verifyToken()
    const status = result.status

    console.log(status)
    if (status === 1002) {
        const result = await refreshToken()
        const refreshed = result.access_token
        return refreshed ? goHome(next) : (to.name !== 'Login' ? goLogin(next) : next())
    }

    if (status === 0) {
        // 已登录访问登录页，跳首页
        return to.name === 'Login' ? goHome(next) : next()
    }

    // 其他情况兜底，且不是登录页才跳登录页
    if (to.name !== 'Login') return goLogin(next)

    next()
}
