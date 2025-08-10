<template>
  <router-view />
</template>
<script setup>
import { ref, onMounted } from 'vue'
// 页面加载时执行，恢复主题
function loadTheme() {
  const savedTheme = localStorage.getItem('theme');
  const html = document.documentElement;
  if (savedTheme === 'dark') {
    html.classList.add('mdui-theme-dark');
    html.classList.remove('mdui-theme-light');
  } else if (savedTheme === 'light') {
    html.classList.add('mdui-theme-light');
    html.classList.remove('mdui-theme-dark');
  } else {
    // 默认主题，如果你想默认暗黑就写下面这句
    // html.classList.add('mdui-theme-dark');
  }
}
onMounted(() => {
  loadTheme()
})
</script>
