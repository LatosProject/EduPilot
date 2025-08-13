<template>
    <div style="
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    ">
        <div style="
        position: relative;
        width: 480px;
        min-height: 320px;
        background-color: rgb(var(--mdui-color-surface-container-lowest));
        box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
        border-radius: var(--mdui-shape-corner-extra-large);
        padding: 24px;
        overflow: hidden;
      ">
            <!-- 绝对定位进度条 -->
            <mdui-linear-progress v-if="isLoading"
                style="position: absolute; left: 24px; top: 0; height: 4px; width: calc(100% - 48px);"></mdui-linear-progress>
            <span style="
          font-family: 'Noto Sans SC';
          font-size: 32px;
          margin-top: 16px;
          display: block;
          white-space: nowrap;
          overflow: hidden;
        ">
                <template v-if="step === 2 && username">{{ username }}</template>
                <template v-else>登录</template>
            </span>
            <span style="
          font-family: 'Noto Sans SC';
          font-size: 16px;
          margin-top: 14px;
          margin-bottom: 24px;
          display: block;
          color: var(--mdui-color-text-secondary);
          white-space: nowrap;
          overflow: hidden;
        ">
                <template v-if="step === 2 && username">如需继续操作，请先验证您的身份</template>
                <template v-else>使用您的 EduPilot 账号</template>
            </span>

            <div class="input-slide-container" style="position: relative; height: 100px;">
                <!-- 用户名输入框 -->
                <form @submit.prevent="handleNext" class="slide-form"
                    :class="{ 'slide-out-left': step === 2, 'slide-in-left': step === 1 }"
                    style="position: absolute; width: 100%;">
                    <mdui-text-field ref="usernameField" :disabled="isUsernameDisabled" style="margin-top: 12px;"
                        :value="username" @input="onUsernameInput" variant="outlined" label="用户名" type="text" />
                </form>

                <!-- 密码输入框 -->
                <form @submit.prevent="handleLogin" class="slide-form"
                    :class="{ 'slide-in-right': step === 2, 'slide-out-right': step === 1 }"
                    style="position: absolute; width: 100%; ">
                    <mdui-text-field ref="passwordField" style="margin-top: 12px;" v-model="password" variant="outlined"
                        @input="onPasswordInput" label="密码" type="password" toggle-password />
                </form>
            </div>

            <div style="
          position: absolute;
          left: 8px;
          bottom: 18px;
          color: rgb(var(--mdui-color-primary-light));
          background-color: transparent;
        ">
                <mdui-button type="button"
                    style="color: rgb(var(--mdui-color-primary-light)); background-color: transparent;"
                    @click="step === 1 ? handleRegister() : handleBack()"> {{ step === 1 ? '注册账号' : '返回'
                    }}</mdui-button>
            </div>

            <div style="position: absolute; right: 18px; bottom: 18px;">
                <mdui-button type="submit" @click="step === 1 ? handleNext() : handleLogin()">
                    {{ step === 1 ? '继续' : '登录' }}
                </mdui-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { login } from '../api/auth'
import 'mdui/components/text-field.js'

const route = useRoute()
const router = useRouter()

const usernameField = ref(null)
const passwordField = ref(null)
const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false);
const step = computed(() => (route.path.endsWith('password') ? 2 : 1))

const onUsernameInput = (e) => {
    username.value = e.target.value
}
const onPasswordInput = (e) => {
    password.value = e.target.value
}

const isUsernameDisabled = computed(() => step.value === 2)

const handleNext = () => {
    error.value = ''
    if (!username.value) {
        usernameField.value?.setCustomValidity('用户名不能为空')
        usernameField.value?.reportValidity()
        return
    }
    usernameField.value?.setCustomValidity('')
    usernameField.value?.reportValidity()
    router.push('/login/password')
}

const handleBack = () => {
    router.push('/login')
}

let lastClickTime = 0
const handleLogin = async () => {
    const now = Date.now()
    if (now - lastClickTime < 1000) return
    lastClickTime = now
    if (isLoading.value) return   // 正在处理就直接返回
    isLoading.value = true;
    error.value = ''
    if (!password.value) {
        passwordField.value?.setCustomValidity('密码不能为空')
        passwordField.value?.reportValidity()
        isLoading.value = false;
        return
    }
    passwordField.value?.setCustomValidity('')
    passwordField.value?.reportValidity()

    try {
        const res = await login(username.value, password.value)
        const token = res.data?.data?.access_token
        if (token) {
            localStorage.setItem('access_token', token)
            router.push('/')
        } else {
            passwordField.value?.setCustomValidity('登录失败，请重试')
            passwordField.value?.reportValidity()
            isLoading.value = false;
        }
    } catch (err) {
        if (err.response && err.response.data) {
            passwordField.value?.setCustomValidity(err.response.data.message)
            passwordField.value?.reportValidity()
            isLoading.value = false;
        }
    }
}

const handleRegister = () => {
    alert('此网站暂未开放，请联系网络管理员。')
}

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

onMounted(async () => {
    if (step.value === 2 && !username.value) {
        router.replace('/login')
    }
})
</script>

<style scoped>
.input-slide-container {
    overflow: hidden;
    height: 80px;
    /* 适应输入框高度 */
    position: relative;
}

.slide-form {
    transition: transform 0.4s ease, opacity 0.4s ease;
}

/* 用户名输入框进入和退出 */
.slide-in-left {
    transform: translateX(0);
    opacity: 1;
}

.slide-out-left {
    transform: translateX(-100%);
    opacity: 0;
}

/* 密码输入框进入和退出 */
.slide-in-right {
    transform: translateX(0);
    opacity: 1;
}

.slide-out-right {
    transform: translateX(100%);
    opacity: 0;
}

mdui-text-field::part(label) {
    background-color: rgb(var(--mdui-color-surface-container-lowest));
}
</style>
