<template>

  <div class="submission-card">
    <div style="height: calc(100vh - 344px);"
      ref="editorRef"
      class="editor"
      contenteditable
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    ></div>

    <div v-if="showHint" class="placeholder">
      轻触以编辑……
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";

const props = defineProps({
  modelValue: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["update:modelValue"]);

const editorRef = ref(null);
const showHint = ref(true);

onMounted(() => {
  if (props.modelValue) {
    editorRef.value.innerText = props.modelValue;
    showHint.value = false;
  }
});

function onInput() {
  const text = editorRef.value.innerText.trim();
  emit("update:modelValue", text);
  showHint.value = text.length === 0;
}

function onFocus() {
  showHint.value = false;
}

function onBlur() {
  if (!editorRef.value.innerText.trim()) {
    showHint.value = true;
  }
}

watch(
  () => props.modelValue,
  (val) => {
    if (!val && editorRef.value) {
      editorRef.value.innerText = "";
      showHint.value = true;
    }
  }
);
</script>

<style scoped>
.submission-card {
  position: relative;
  padding: 0
}

.editor {
  min-height: 120px;
  outline: none;
  font-size: 15px;
  line-height: 1.6;
  background: transparent;
  caret-color: rgb(var(--mdui-color-primary));
}

.placeholder {
  position: absolute;
  top: 0;
  left: 0;
  color: rgb(var(--mdui-color-on-surface-variant));
  pointer-events: none;
  line-height: 1.6; /* 和编辑器一致，保证垂直对齐 */
}

</style>
