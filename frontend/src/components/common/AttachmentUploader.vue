<script setup>
import { ref, watch, defineExpose } from "vue";

// 文件大小限制：100MB
const MAX_FILE_SIZE = 100 * 1024 * 1024;

// 允许的文件扩展名（与后端保持一致）
const ALLOWED_EXTENSIONS = new Set([
  // 文档
  ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".rtf", ".odt", ".ods", ".odp", ".csv",
  // 图片
  ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff", ".tif", ".heic", ".heif",
  // 压缩包
  ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
  // 代码
  ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".sass", ".less",
  ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php",
  ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".conf", ".cfg",
  ".sql", ".sh", ".bat", ".ps1", ".vue", ".svelte",
  // 其他媒体
  ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4a", ".flac", ".ogg",
]);

// 获取文件扩展名（小写）
function getFileExtension(filename) {
  const lastDot = filename.lastIndexOf(".");
  return lastDot >= 0 ? filename.slice(lastDot).toLowerCase() : "";
}

// 父组件传递过来的 `files`
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
});
const emit = defineEmits(["update:modelValue", "error"]); // 用于更新父组件的 `files`

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

// 格式化文件大小显示
function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

// 处理文件选择
function onChange(e) {
  const selected = Array.from(e.target.files);
  const oversizedFiles = [];
  const unsupportedFiles = [];
  const validFiles = [];

  // 检查文件大小和类型
  selected.forEach((file) => {
    const ext = getFileExtension(file.name);
    if (!ALLOWED_EXTENSIONS.has(ext)) {
      unsupportedFiles.push(file.name);
    } else if (file.size > MAX_FILE_SIZE) {
      oversizedFiles.push(file.name);
    } else {
      validFiles.push(file);
    }
  });

  // 如果有不支持的文件类型，发出错误事件
  if (unsupportedFiles.length > 0) {
    emit("error", {
      type: "type",
      message: `不支持的文件类型：${unsupportedFiles.join(", ")}`,
      files: unsupportedFiles,
    });
  }

  // 如果有超过大小限制的文件，发出错误事件
  if (oversizedFiles.length > 0) {
    emit("error", {
      type: "size",
      message: `以下文件超过 100MB 限制：${oversizedFiles.join(", ")}`,
      files: oversizedFiles,
    });
  }

  // 去重：只添加尚未存在的文件
  validFiles.forEach((file) => {
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
defineExpose({ pick, clear, formatFileSize });
</script>

<template>
  <div>
    <!-- 文件输入框 -->
    <input ref="input" type="file" multiple hidden @change="onChange" />
  </div>
</template>
