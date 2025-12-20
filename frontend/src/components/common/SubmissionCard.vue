<template>
  <div>
    <!-- 文本编辑器 -->
    <TextEditor v-model="contentValue"  />
    <!-- 附件列表组件 -->
    <AttachmentUploader ref="uploader" v-model="attachmentsValue" />

    <div class="actions" v-if="showActions"></div>


  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import TextEditor from "./TextEditor.vue";
import AttachmentUploader from "./AttachmentUploader.vue";
import { setTheme } from "mdui/functions/setTheme.js";
import { getTheme } from "mdui/functions/getTheme.js";
import { defineExpose } from "vue";

const props = defineProps({
  attachments: { type: Array, default: () => [] },
  content: { type: String, default: "" },
  showActions: { type: Boolean, default: true },
});
const emit = defineEmits(["update:attachments", "update:content", "submit"]);

const attachmentsValue = ref([...props.attachments]);
const contentValue = ref(props.content);

const uploader = ref(null);

// 双向绑定
watch(attachmentsValue, (val) => emit("update:attachments", val));
watch(contentValue, (val) => emit("update:content", val));

function onSubmit() {
  emit("submit", {
    content: contentValue.value,
    attachments: attachmentsValue.value,
  });
}

// 调用 AttachmentUploader 内部方法
function triggerUpload() {
  if (uploader.value && uploader.value.pick) {
    uploader.value.pick();
  }
}

function toggleTheme() {
  let theme = getTheme();
  if (theme === "auto") {
    const prefersDark = window.matchMedia(
      "(prefers-color-scheme: dark)"
    ).matches;
    theme = prefersDark ? "dark" : "light";
  }

  if (theme === "dark") {
    setTheme("light");
    localStorage.setItem("theme", "light");
  } else {
    setTheme("dark");
    localStorage.setItem("theme", "dark");
  }
}
function clearAttachments() {
  attachmentsValue.value = [];
  if (uploader.value && uploader.value.clear) {
    uploader.value.clear();
  }
}

defineExpose({
  triggerUpload,
  onSubmit,
  clearAttachments,
});

</script>
