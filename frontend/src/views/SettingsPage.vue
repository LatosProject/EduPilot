<template>
  <!-- 页面整体横向布局 -->
  <div style="display: flex; height: 100vh;">
    <!-- 左侧导航栏 -->
    <NavigationRail />
    <div style="
          margin-top: 24px;
          min-width: 480px;
          flex-grow: 1;
          margin-left: 16px;
          margin-right: 24px;
          background-color: rgb(var(--mdui-color-surface-container-lowest));
          box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.20);
          border-radius: var(--mdui-shape-corner-extra-large);
        ">
      <div style="margin-left: 48px">
        <div class="mdui-prose" style="margin-top: 48px;">
          <div>
            <h2>通用</h2>
          </div>
          <div
            style="width: 680px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
            跟随系统主题
            <mdui-switch id="themeSwitch" checked ref="themeSwitch"></mdui-switch>
          </div>
          <div
            style="width: 680px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
            🏳‍🌈
            <mdui-switch></mdui-switch>
          </div>
          <div
            style="width: 680px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
            访问源代码
            <mdui-button-icon href="https://github.com/LatosProject/EduPilot" icon="open_in_new"></mdui-button-icon>
          </div>
          <div style="margin-top: 24px;">
            <mdui-tooltip content="您确定要登出吗？">
              <mdui-button @click="logout">登出</mdui-button></mdui-tooltip>
          </div>

        </div>
        <footer style="text-align: left; font-size: 12px; color: #888; padding: 8px 0;">
          © 2025 EduPilot, Latos. All rights reserved.
        </footer>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import NavigationRail from '../components/common/NavigationRail.vue'
import { useRouter } from 'vue-router'
import { setTheme } from 'mdui/functions/setTheme.js';
const router = useRouter()
const themeSwitch = ref(null) // 用ref绑定元素

function logout() {
  localStorage.removeItem('access_token')
  router.push('/login')
}

onMounted(() => {
  // 初始化开关状态和主题
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'auto') {
    themeSwitch.value.checked = true
  } else {
    themeSwitch.value.checked = false
  }

  // 绑定事件，响应用户操作
  themeSwitch.value.addEventListener('change', () => {
    if (themeSwitch.value.checked) {
      setTheme('auto')
      localStorage.setItem('theme', 'auto')
    } else {
      setTheme('light')
      localStorage.setItem('theme', 'light')
    }
  })
})

</script>