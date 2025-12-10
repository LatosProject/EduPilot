<template>
    <!-- 整体外层：居中布局，撑满整个视口高度 -->
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
        <!-- 卡片容器：固定宽度、圆角、阴影、内边距等 -->
        <div style="position: relative; width: 480px; min-height: 320px; background-color: rgb(var(--mdui-color-surface-container-lowest)); box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2); border-radius: var(--mdui-shape-corner-extra-large); padding: 24px; overflow: hidden;">

            <!-- 顶部加载进度条（仅在 isLoading 时显示） -->
            <mdui-linear-progress v-if="isLoading" style="position: absolute; left: 24px; top: 0; height: 4px; width: calc(100% - 48px);"></mdui-linear-progress>

            <!-- 主标题：根据 step 显示用户名或“登录”字样 -->
            <span style="font-family: 'Noto Sans SC'; font-size: 32px; margin-top: 16px; display: block; white-space: nowrap; overflow: hidden;">
                <template v-if="step === 2 && username">{{ username }}</template>
                <template v-else>登录</template>
            </span>

            <!-- 副标题：提示语随步骤切换 -->
            <span style="font-family: 'Noto Sans SC'; font-size: 16px; margin-top: 14px; margin-bottom: 24px; display: block; color: var(--mdui-color-text-secondary); white-space: nowrap; overflow: hidden;">
                <template v-if="step === 2 && username">如需继续操作，请先验证您的身份</template>
                <template v-else>使用您的 EduPilot 账号</template>
            </span>

            <!-- 输入区：包含滑动动画效果的用户名与密码输入框 -->
            <div class="input-slide-container" style="position: relative; height: 100px;">

                <!-- 用户名输入表单（步骤 1） -->
                <form @submit.prevent="handleNext" class="slide-form" :class="{ 'slide-out-left': step === 2, 'slide-in-left': step === 1 }" style="position: absolute; width: 100%;">
                    <mdui-text-field ref="usernameField" :disabled="isUsernameDisabled" style="margin-top: 12px;" :value="username" @input="onUsernameInput" variant="outlined" label="用户名" type="text" />
                </form>

                <!-- 密码输入表单（步骤 2） -->
                <form @submit.prevent="handleLogin" class="slide-form" :class="{ 'slide-in-right': step === 2, 'slide-out-right': step === 1 }" style="position: absolute; width: 100%; ">
                    <mdui-text-field ref="passwordField" style="margin-top: 12px;" v-model="password" variant="outlined" @input="onPasswordInput" label="密码" type="password" toggle-password />
                </form>
            </div>

            <!-- 左下角按钮：注册或返回 -->
            <div style="position: absolute; left: 8px; bottom: 18px; color: rgb(var(--mdui-color-primary-light)); background-color: transparent;">
                <mdui-button type="button" style="color: rgb(var(--mdui-color-primary-light)); background-color: transparent;" @click="step === 1 ? handleRegister() : handleBack()">{{ step === 1 ? '注册账号' : '返回' }}</mdui-button>
            </div>

            <!-- 右下角按钮：继续或登录 -->
            <div style="position: absolute; right: 18px; bottom: 18px;">
                <mdui-button type="submit" @click="step === 1 ? handleNext() : handleLogin()">{{ step === 1 ? '继续' : '登录' }}</mdui-button>
            </div>
        </div>
    </div>
</template>

<script setup>
// 引入 Vue 工具函数与路由模块
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 引入登录 API
import { login } from '../api/auth'

// 引入 mdui 文本框组件
import 'mdui/components/text-field.js'

// 全局状态管理
import { useGlobalStore } from '../stores/global'

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()

// 输入框引用，用于操作组件内部方法
const usernameField = ref(null)
const passwordField = ref(null)

// 响应式字段：用户名、密码、错误信息、加载状态
const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

// 当前步骤：根据路由路径计算（/login → step 1，/login/password → step 2）
const step = computed(() => (route.path.endsWith('password') ? 2 : 1))

// 输入事件：手动写入触发的值
const onUsernameInput = (e) => {
    username.value = e.target.value
}
const onPasswordInput = (e) => {
    password.value = e.target.value
}

// 用户名是否禁用（第二步需要禁用）
const isUsernameDisabled = computed(() => step.value === 2)

// 下一步（从用户名 → 密码）
const handleNext = () => {
    error.value = ''

    // 校验用户名非空
    if (!username.value) {
        usernameField.value?.setCustomValidity('用户名不能为空')
        usernameField.value?.reportValidity()
        return
    }

    // 清除校验提示
    usernameField.value?.setCustomValidity('')
    usernameField.value?.reportValidity()

    // 进入密码页面
    router.push('/login/password')
}

// 返回上一步（清空密码）
const handleBack = () => {
    password.value = ''
    router.push('/login')
}

// 防抖：限制重复点击（1 秒内只允许一次）
let lastClickTime = 0

// 登录流程
const handleLogin = async () => {
    const now = Date.now()

    // 按钮点击限频
    if (now - lastClickTime < 1000) return
    lastClickTime = now

    if (isLoading.value) return
    isLoading.value = true
    error.value = ''

    // 校验密码
    if (!password.value) {
        passwordField.value?.setCustomValidity('密码不能为空')
        passwordField.value?.reportValidity()
        isLoading.value = false
        return
    }

    passwordField.value?.setCustomValidity('')
    passwordField.value?.reportValidity()

    // 调用登录 API
    try {
        const res = await login(username.value, password.value)
        const token = res.data?.data?.access_token

        if (token) {
            // 保存 token
            localStorage.setItem('access_token', token)
            router.push('/')
        } else {
            // 登录失败提示
            passwordField.value?.setCustomValidity('登录失败，请重试')
            passwordField.value?.reportValidity()
            isLoading.value = false
        }
    } catch (err) {
        // API 错误信息
        if (err.response && err.response.data) {
            passwordField.value?.setCustomValidity(err.response.data.message)
            passwordField.value?.reportValidity()
            isLoading.value = false
        }
    }
}

// 注册提示
const handleRegister = () => {
    alert('此网站暂未开放，请联系网络管理员。')
}

// 监视步骤变化：进入 step2 时自动聚焦密码框
watch(step, async (newStep) => {
    if (newStep === 2 && !username.value) {
        router.replace('/login')
    }

    if (newStep === 2) {
        await nextTick()
        setTimeout(() => {
            passwordField.value?.focus()
        }, 450)
    }
})

// 初始挂载逻辑
onMounted(async () => {
    // 直接访问 /login/password 且用户名为空 → 返回输入用户名
    if (step.value === 2 && !username.value) {
        router.replace('/login')
    }

    // 已登录且已加入班级 → 首页
    if (globalStore.classUuids.length && localStorage.getItem('access_token') !== null) {
        router.replace({ name: 'Home' })
        return
    }

    // 已登录但未加入班级 → 邀请页
    if (!globalStore.classUuids.length && localStorage.getItem('access_token') !== null) {
        router.replace({ name: 'Invite' })
        return
    }
})
</script>

<style scoped>
/* 输入区域容器：用于遮挡滑动动画 */
.input-slide-container {
    overflow: hidden;
    height: 80px;
    position: relative;
}

/* 表单滑动动画 */
.slide-form {
    transition: transform 0.4s ease, opacity 0.4s ease;
}

.slide-in-left {
    transform: translateX(0);
    opacity: 1;
}

.slide-out-left {
    transform: translateX(-100%);
    opacity: 0;
}

.slide-in-right {
    transform: translateX(0);
    opacity: 1;
}

.slide-out-right {
    transform: translateX(100%);
    opacity: 0;
}

/* mdui 文本框标签背景修正 */
mdui-text-field::part(label) {
    background-color: rgb(var(--mdui-color-surface-container-lowest));
}
</style>