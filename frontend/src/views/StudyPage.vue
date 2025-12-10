<template>
  <!-- 页面整体横向布局 -->
  <div style="display: flex; height: 100vh">
    <!-- 左侧导航栏 -->
    <NavigationRail />
  </div>
</template>
<script setup>
import NavigationRail from "../components/common/NavigationRail.vue";
import { onMounted } from "vue";
import { useGlobalStore } from '../stores/global';
import { useRouter } from 'vue-router'

const globalStore = useGlobalStore()
const router = useRouter()

// 页面挂载初始化
onMounted(() => {
  // 已登录但未加入班级 → 邀请页
  if (!globalStore.classUuids.length && localStorage.getItem('access_token') !== null) {
    router.replace({ name: 'Invite' })
    return
  }
})
</script>
