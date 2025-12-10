<template>
  <!-- 整体容器：可根据导航宽度动态调整 padding -->
  <div :style="{ paddingLeft: contentPaddingLeft + 'px', transition: 'padding-left 0.3s' }">
    <div style="display: flex; height: 100vh;">
      
      <!-- 左侧导航栏 -->
      <NavigationRail @menu-click="onMenuClick" />

      <!-- 右侧主要内容区域 -->
      <div
        style="
          margin-top: 24px;
          min-width: 480px;
          flex-grow: 1;
          margin-left: 8px;
          margin-right: 24px;
          background-color: rgb(var(--mdui-color-surface-container-lowest));
          box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.20);
          border-radius: var(--mdui-shape-corner-extra-large);
          margin-bottom: 24px;
        "
      >
        <div style="margin-left: 48px;">
          <div class="mdui-prose" style="margin-top: 48px;">

            <!-- 通用设置标题 -->
            <div>
              <h2>通用</h2>
            </div>

            <!-- 跟随系统主题开关 -->
            <div style="width: 600px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
              跟随系统主题
              <mdui-switch id="themeSwitch" checked ref="themeSwitch"></mdui-switch>
            </div>

            <!-- 设置主题色 -->
            <div style="width: 600px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
              设置主题色
              <mdui-button-icon icon="open_in_new" @click="openColorPickerDialog"></mdui-button-icon>
            </div>

            <!-- 访问源代码 -->
            <div style="width: 600px; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
              访问源代码
              <mdui-button-icon href="https://github.com/LatosProject/EduPilot" icon="open_in_new"></mdui-button-icon>
            </div>

            <!-- 登出按钮 -->
            <div style="margin-top: 24px;">
              <mdui-tooltip content="您确定要登出吗？">
                <mdui-button @click="logout">登出</mdui-button>
              </mdui-tooltip>
            </div>

          </div>

          <!-- 页脚信息 -->
          <footer style="text-align: left; font-size: 12px; color: #888; padding: 8px 0;">
            版本 0.1 Beta
          </footer>
          <footer style="text-align: left; font-size: 12px; color: #888; padding: 8px 0;">
            © 2025 EduPilot, Latos. All rights reserved.
          </footer>

          <!-- 颜色选择器弹窗 -->
          <mdui-dialog ref="colorPickerDialog" class="colorPickerDialog" close-on-overlay-click close-on-esc>
            <div style="max-width: 320px; overflow: hidden;" id="picker"></div>
          </mdui-dialog>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import NavigationRail from '../components/common/NavigationRail.vue'
import { logoutApi } from '../api/auth'
import { setTheme } from 'mdui/functions/setTheme.js';
import { setColorScheme } from 'mdui/functions/setColorScheme.js';
import iro from '@jaames/iro';
import { useGlobalStore } from '../stores/global'

const globalStore = useGlobalStore()
// 路由
const router = useRouter()

// ref 对象
const themeSwitch = ref(null)
const colorPickerDialog = ref(null)

// 导航栏 toggle
const toggle = ref(localStorage.getItem("navToggle") === "1")
const contentPaddingLeft = ref(toggle.value ? 48 : 8)

// 切换导航栏宽度
function onMenuClick() {
  toggle.value = !toggle.value
  localStorage.setItem("navToggle", toggle.value ? "1" : "0")
  contentPaddingLeft.value = toggle.value ? 48 : 8
}

// 登出逻辑
function logout() {
  localStorage.removeItem('access_token')
  router.replace({ name: 'Login' })
  logoutApi()
}

// 打开颜色选择器弹窗
function openColorPickerDialog() {
  if (colorPickerDialog.value) {
    colorPickerDialog.value.open = true
  }
}

// 页面挂载初始化
onMounted(() => {
  // 初始化颜色选择器
  let savedThemeColor = localStorage.getItem('themeColor')
  const colorPicker = new iro.ColorPicker("#picker", {
    width: 320,
    borderWidth: 2,
    color: savedThemeColor,
  }
)

  // 设置初始主题色
  setColorScheme(savedThemeColor)

  // 监听颜色变化，实时更新主题色
  colorPicker.on('color:change', (color) => {
    setColorScheme(color.hexString)
    localStorage.setItem('themeColor', color.hexString)
  })

  // 初始化开关状态和主题
  const savedTheme = localStorage.getItem('theme')
  themeSwitch.value.checked = savedTheme === 'auto'

  // 开关事件：切换自动 / 浅色主题
  themeSwitch.value.addEventListener('change', () => {
    if (themeSwitch.value.checked) {
      setTheme('auto')
      localStorage.setItem('theme', 'auto')
    } else {
      setTheme('light')
      localStorage.setItem('theme', 'light')
    }
  })
    // 已登录但未加入班级 → 邀请页
    if (!globalStore.classUuids.length && localStorage.getItem('access_token') !== null) {
        router.replace({ name: 'Invite' })
        return
    }
})
</script>
