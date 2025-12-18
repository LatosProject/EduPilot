<script setup>
import { ref, defineExpose } from "vue";

const props = defineProps({ modelValue: Array });
const emit = defineEmits(["update:modelValue"]);

const files = ref([...props.modelValue]);
const input = ref(null);

function pick() {
  input.value.click();
}

function onChange(e) {
  const selected = Array.from(e.target.files);
  files.value.push(...selected);
  emit("update:modelValue", files.value);
}

function remove(i) {
  files.value.splice(i, 1);
  emit("update:modelValue", files.value);
}

// 暴露 pick 方法给外部调用
defineExpose({ pick });
</script>

<template>
  <div>
    <ul>
      <li v-for="(file, i) in files" :key="i">
        {{ file.name }}
        <mdui-button-icon icon="close" @click="remove(i)" />
      </li>
    </ul>
    <input ref="input" type="file" multiple hidden @change="onChange" />
  </div>
</template>
