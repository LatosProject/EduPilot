<template>
  <mdui-navigation-rail ref="railRef" style="padding-top: 8px" contained>
    <mdui-button-icon icon="menu" slot="top"></mdui-button-icon>
    <mdui-fab class="fab-purple" lowered icon="edit--rounded" slot="top"></mdui-fab>
    <mdui-navigation-rail-item v-for="item in navItems" :key="item.path" class="label-medium secondary"
      :icon="item.icon" :value="item.value" @click="go(item)">
      <mdui-badge v-if="item.path === '/' && globalStore.homeBadge > 0" slot="badge">
        {{ globalStore.homeBadge > 99 ? '99+' : globalStore.homeBadge }}
      </mdui-badge>
      {{ item.label }}
    </mdui-navigation-rail-item>
  </mdui-navigation-rail>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

import { onMounted, watch, ref } from 'vue'
import { useGlobalStore } from '/src/stores/global.js'
const router = useRouter()
const route = useRoute()
const railRef = ref(null)
const globalStore = useGlobalStore()
const homeBadge = globalStore.homeBadge

const navItems = [
  { label: '主页', path: '/', icon: 'inbox--rounded', value: 'home' },
  { label: '学习', path: '/study', icon: 'book--rounded', value: 'study' },
  { label: '设置', path: '/settings', icon: 'settings--rounded', value: 'setting' }
]

// 点击时跳转
function go(item) {
  router.push(item.path)
}

// 路由 → 选中 value
function syncActiveValue(path) {
  const found = navItems.find(i => i.path === path)
  if (railRef.value) {
    railRef.value.value = found ? found.value : 'home'
  }
}

onMounted(() => {
  // 初始化
  syncActiveValue(route.path)
})

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
    syncActiveValue(newPath)
  }
)
</script>

<style scoped>
/* .fab-purple {
  background-color: purple;
  color: white;
} */
</style>
