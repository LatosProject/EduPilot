<template>
  <div :class="['tip', data.style]" style="margin-top: 8px; margin-bottom: 8px; margin-right: 8px;">
    <div class="icon">
      <mdui-icon v-if="data.style === 'warning'">warning</mdui-icon>
      <mdui-icon v-else-if="data.style === 'info'">info</mdui-icon>
      <mdui-icon v-else-if="data.style === 'success'">check_circle</mdui-icon>
    </div>
    <div class="content">{{ data.content }}</div>
  </div>
</template>

<script setup>
defineProps({ data: Object })
</script>

<style scoped>
.tip {
  display: flex;
  align-items: flex-start;
  gap: 8px; /* 图标和文字间距 */
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  max-width: 320px;
}

.tip.warning {
  background-color: #fff4e5;
  color: #663c00;
}

.tip.info {
  background-color: #e5f6fd;
  color: #004d6a;
}

.tip.success {
  background-color: #e6f4ea;
  color: #1b5e20;
}

.icon {
  font-size: 24px;
  line-height: 1;
}

.content {
  flex: 1;
}
</style>
