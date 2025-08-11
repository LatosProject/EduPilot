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
            style="width: 600px ; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
            跟随系统主题
            <mdui-switch id="themeSwitch" checked ref="themeSwitch"></mdui-switch>
          </div>
          <div style=" width: 600px ; margin-top: 24px; display: flex; align-items: center; justify-content:
            space-between;">
            设置主题色
            <mdui-button-icon icon="open_in_new" @click="openColorPickerDialog"></mdui-button-icon>
          </div>
          <div
            style="width: 600px ; margin-top: 24px; display: flex; align-items: center; justify-content: space-between;">
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

        <mdui-dialog ref="colorPickerDialog" class="colorPickerDialog" close-on-overlay-click close-on-esc>
          <div style="max-width: 320px" id="picker"></div>
        </mdui-dialog>

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
const colorPickerDialog = ref(null)
import iro from '@jaames/iro';
import { setColorScheme } from 'mdui/functions/setColorScheme.js';


function logout() {
  localStorage.removeItem('access_token')
  router.push('/login')
}
function openColorPickerDialog() {
  if (colorPickerDialog.value) {
    colorPickerDialog.value.open = true
  }
}
onMounted(() => {
  let savedThemeColor = localStorage.getItem('themeColor');
  var colorPicker = new iro.ColorPicker("#picker", {
    width: 320,
    color: savedThemeColor
  });
  setColorScheme(savedThemeColor);


  // 监听颜色变化，实时更新主题色
  colorPicker.on('color:change', (color) => {
    setColorScheme(color.hexString);
    localStorage.setItem('themeColor', color.hexString);  // 可选，保存用户选色
  });


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