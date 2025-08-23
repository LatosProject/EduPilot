// src/router/guards.js

// 从认证服务中导入相关方法和常量

import {
    getAccessToken,
    refreshToken,
    verifyToken
} from '../api/auth'

// 跳转到登录页的辅助函数
function goLogin(next) {
    return next({ name: 'Login' })
}

// 跳转到首页的辅助函数
function goHome(next) {
    return next({ name: 'Home' })
}

export async function authGuard(to, from, next) {
    const token = getAccessToken()

    // 登录页不需要验证 token，直接放行
    if (to.name === 'Login') return next()

    // 没有 token，直接跳登录页
    if (!token) return next({ name: 'Login' })

    try {
        const { status } = await verifyToken()

        if (status === 1002) { // token 过期
            const refresh = await refreshToken()
            if (refresh?.access_token) return next()  // 刷新成功
            // 刷新失败，直接去登录页，注意不要再尝试刷新
            return next({ name: 'Login' })
        }

        if (status === 0) return next() // token 有效，放行

        // 其他情况，直接跳登录页
        return next({ name: 'Login' })

    } catch (err) {
        // 网络或异常，也直接跳登录页
        return next({ name: 'Login' })
    }
}
