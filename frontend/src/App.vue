<template>
  <router-view />
</template>
<script setup>
import { onMounted } from 'vue'
import { setTheme } from 'mdui/functions/setTheme.js';
import { setColorScheme } from 'mdui/functions/setColorScheme.js';
// 页面加载时执行，恢复主题
function loadTheme() {
  const savedTheme = localStorage.getItem('theme');
  let savedThemeColor = localStorage.getItem('themeColor');
  if (!savedThemeColor) {
    savedThemeColor = '#2962FF'; // 默认颜色
  }
  setColorScheme(savedThemeColor)
  if (savedTheme === 'dark') {
    setTheme('dark');
  } else if (savedTheme === 'light') {
    setTheme('light');
  } else {
    // 没有保存偏好，或是 auto，采用跟随系统
    setTheme('auto');
  }
}

onMounted(() => {
  loadTheme()
})
</script>
