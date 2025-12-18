<template>
  <div class="submission-card">
    <!-- 编辑器外层滚动容器 -->
    <OverlayScrollbarsComponent
      ref="scrollRef"
      :options="options"
      class="editor-scroll"
    >
      <div
        ref="editorRef"
        class="editor"
        contenteditable
        @input="onInput"
        @focus="onFocus"
        @blur="onBlur"
      ></div>
    </OverlayScrollbarsComponent>

    <!-- 占位提示 -->
    <div v-if="showHint" class="placeholder">轻触以编辑……</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { OverlayScrollbarsComponent } from "overlayscrollbars-vue";
import "overlayscrollbars/styles/overlayscrollbars.css";

const props = defineProps({
  modelValue: { type: String, default: "" },
});
const emit = defineEmits(["update:modelValue"]);

const editorRef = ref(null);
const scrollRef = ref(null);
const showHint = ref(true);

const options = {
  scrollbars: { autoHide: "leave", autoHideDelay: 500 },
};

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
</script>

<style scoped>
.submission-card {
  position: relative;
  height: 100%;
  box-sizing: border-box;
}

/* 滚动容器：固定高度，负责滚动 */
.editor-scroll {
  height: 100%;
  width: 100%;
}

/* 编辑器：让内容自然增长 */
.editor {
  max-height: calc(100vh - 336px);

  outline: none;
  font-size: 15px;
  line-height: 1.6;
  background: transparent;
  caret-color: rgb(var(--mdui-color-primary));

  /* 关键：防止不换行 */
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
  box-sizing: border-box;
}

/* 占位 */
.placeholder {
  position: absolute;
  top: -8px;
  left: -8px;
  margin-left: 8px;
  margin-top: 8px;
  color: rgb(var(--mdui-color-on-surface-variant));
  pointer-events: none;
  line-height: 1.6;
}
</style>
