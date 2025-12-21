<script setup>
import { ref, watch, defineExpose } from "vue";

// 父组件传递过来的 `files`
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
});
const emit = defineEmits(["update:modelValue"]); // 用于更新父组件的 `files`

// 本地副本，用于操作文件
const files = ref([]);

// 监听 `modelValue` 变化，更新本地 `files`
watch(
  () => props.modelValue,
  (newVal) => {
    files.value = Array.isArray(newVal) ? [...newVal] : [];
  },
  { immediate: true }
);

const input = ref(null);

// 打开文件选择框
function pick() {
  input.value.click();
}

// 处理文件选择
function onChange(e) {
  const selected = Array.from(e.target.files);

  // 去重：只添加尚未存在的文件
  selected.forEach((file) => {
    if (
      !files.value.some((f) => f.name === file.name && f.size === file.size)
    ) {
      files.value.push(file);
    }
  });

  // 更新父组件的 `files`
  emit("update:modelValue", files.value);
  console.log(files.value);

  // 清空 input 的值，以便允许选择相同文件再次触发 change 事件
  if (input.value) input.value.value = "";
}

// 删除文件
function remove(i) {
  files.value.splice(i, 1); // 删除文件
  emit("update:modelValue", files.value); // 更新父组件的 `files`
}

// 清空文件列表
function clear() {
  files.value = [];
  emit("update:modelValue", files.value);
  if (input.value) input.value.value = "";
}

// 暴露 pick 和 clear 方法给外部调用
defineExpose({ pick, clear });
</script>

<template>
  <div>
    <!-- 文件输入框 -->
    <input ref="input" type="file" multiple hidden @change="onChange" />
  </div>
</template>
