<template>
  <div style="
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 2px;
      margin-top: 16px;
    ">
    <mdui-button v-for="(btn, i) in buttons" :key="i" :variant="btn.selected ? 'filled' : 'tonal'"
      :icon="btn.selected ? 'star' : ''" style="flex: 1" @click="selectButton(i)">
      {{ btn.label }}
    </mdui-button>
  </div>
</template>

<script setup>
import { reactive, defineEmits } from 'vue';

const emit = defineEmits(['status-change']);

const buttons = reactive([
  { label: '总作业', status: '', selected: true },
  { label: '待完成', status: 'pending', selected: false },
  { label: '已完成', status: 'done', selected: false },
  { label: '已过期', status: 'expired', selected: false },
]);

function selectButton(index) {
  buttons.forEach((btn, i) => {
    btn.selected = i === index;
  });
  // 找出选中按钮对应的 status，发给父组件
  const selectedStatus = buttons[index].status;
  emit('status-change', selectedStatus);
}
</script>
