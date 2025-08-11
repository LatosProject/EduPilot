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
            <mdui-switch></mdui-switch>
          </div>
          <div
            style="width: 680px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
            🏳‍🌈
            <mdui-switch></mdui-switch>
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
import NavigationRail from '../components/common/NavigationRail.vue'
function logout() {
  // 1. 清除本地存储
  localStorage.removeItem('access_token')
  // 2. 跳转到登录页
  router.push('/login')
}

</script>