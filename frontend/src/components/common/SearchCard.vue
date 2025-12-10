<template>
  <div style="position: relative; width: 100%;">
    <!-- 搜索卡片 -->
    <mdui-card ref="cardRef" :class="{ 'card-focused': isEditing }" style="
        cursor: text;
        border-radius: var(--mdui-shape-corner-extra-large);
        height: 48px;
        display: flex;
        align-items: center;
        padding: 0;
        gap: 0;
        background-color: rgb(var(--mdui-color-surface-container-high));
      " @click="startEditing">
      <!-- 搜索图标 -->
      <mdui-icon name="search" style="
          font-size: 24px;
          color: rgb(var(--mdui-color-on-surface-variant));
          user-select: none;
          margin: 0 16px;
        "></mdui-icon>

      <!-- 输入框 -->
      <input ref="searchInput" v-model="keyword" placeholder="搜索" style="
          flex: 1;
          font-size: 16px;
          line-height: 56px;
          letter-spacing: 0.5px;
          font-weight: 400;
          font-family: 'Noto Sans SC';
          color: rgb(var(--mdui-color-on-surface-variant));
          border: none;
          outline: none;
          background: transparent;
          padding: 0;
          margin: 0;
        " @focus="isEditing = true" @blur="onBlur" @input="onInput" @keydown="onKeydown"
        @keydown.enter.prevent="emitSearch" />

      <!-- 用户头像 -->
      <template v-if="user && user.avatar_url">
        <mdui-button-icon style="margin-left: auto; margin-right: 8px">
          <img :src="user.avatar_url" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;"
            alt="avatar" />
        </mdui-button-icon>

      </template>
      <template v-else>
        <mdui-button-icon icon="account_circle" style="margin-left: auto; margin-right: 8px"></mdui-button-icon>
      </template>
    </mdui-card>

    <!-- 下拉建议框 -->
    <div v-if="showSuggestions" ref="suggestionBox" style="
        position: absolute;
        top: 60px;
        left: 0;
        right: 0;
        background: rgb(var(--mdui-color-surface-container-lowest));
        border-radius: var(--mdui-shape-corner-medium);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        overflow: auto;
        max-height: 300px;
      ">
      <!-- 有搜索结果 -->
      <template v-if="suggestions.length > 0">
        <div v-for="(item, index) in suggestions" :key="index" @mousedown.prevent="selectSuggestion(item)"
          @mouseenter="hoverIndex = index" :style="{
            backgroundColor:
              hoverIndex === index
                ? 'rgb(var(--mdui-color-surface-container-highest))'
                : 'transparent',
            padding: '10px 16px',
            cursor: 'pointer',
          }" :ref="hoverIndex === index ? 'hoveredItem' : null">
          <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="
                font-size: 15px;
                font-weight: 500;
                color: rgb(var(--mdui-color-on-surface));
              ">{{ item.title }}</span>
            <div style="
                display: flex;
                gap: 12px;
                font-size: 13px;
                color: rgb(var(--mdui-color-on-surface-variant));
              ">
              <span>创建者: {{ item.created_by || '未知' }}</span>
              <span>截止: {{ item.dueDate || '暂无' }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- 无搜索结果 -->
      <template v-else>
        <div style="
            padding: 10px 16px;
            color: rgb(var(--mdui-color-on-surface-variant));
          ">
          未找到相关作业
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from "vue";
import { getProfile } from "../../api/auth";
import { getAssignments } from "../../api/assignment";
import { useGlobalStore } from "../../stores/global";
import { formatDeadline } from "../../utils/date";

const emit = defineEmits(["search"]);
const props = defineProps({
  filterStatus: String
});

const globalStore = useGlobalStore();

// 用户信息
const user = ref(null);

// 输入框状态
const isEditing = ref(false);
const keyword = ref("");
const showSuggestions = ref(false);
const suggestions = ref([]);
const hoverIndex = ref(-1);

// DOM 引用
const searchInput = ref(null);
const suggestionBox = ref(null);

let debounceTimer = null;

// --- 搜索建议 ---
async function fetchSuggestions(query) {
  if (!query.trim()) {
    suggestions.value = [];
    return;
  }

  if (debounceTimer) clearTimeout(debounceTimer);

  debounceTimer = setTimeout(async () => {
    try {
      const results = await Promise.all(
        globalStore.classUuids.map(cls =>
          getAssignments(cls, 1, 10, "created_at", "asc", props.filterStatus)
            .then(res =>
              res.items.map(item => ({
                title: item.title,
                created_by: item.created_by,
                dueDate: formatDeadline(item.deadline),
                uuid: item.uuid,
              }))
            )
            .catch(() => [])
        )
      );

      const lowerQuery = query.toLowerCase();
      suggestions.value = results.flat().filter(item =>
        (item.title && item.title.toLowerCase().includes(lowerQuery)) ||
        (item.created_by && item.created_by.toLowerCase().includes(lowerQuery))
      );
    } catch (err) {
      console.error("获取搜索建议失败:", err);
      suggestions.value = [];
    }
  }, 300);
}

// --- 输入事件 ---
function onInput() {
  showSuggestions.value = true;
  fetchSuggestions(keyword.value);
}

// 选择搜索结果
function selectSuggestion(item) {
  keyword.value = item.title || "";
  showSuggestions.value = false;
  emit("search", item);
}

// 确认搜索
function emitSearch() {
  const val = keyword.value?.trim();
  if (val) {
    emit("search", val);
    showSuggestions.value = false;
  }
}

// 输入框失焦
function onBlur() {
  setTimeout(() => {
    showSuggestions.value = false;
    isEditing.value = false;
  }, 150);
}

// 点击卡片开始编辑
function startEditing() {
  isEditing.value = true;
  if (keyword.value.trim() && suggestions.value.length > 0) {
    showSuggestions.value = true;
    fetchSuggestions(keyword.value);
  }
  nextTick(() => searchInput.value?.focus());
}

// 默认选中第一个建议
watch(suggestions, (newVal) => {
  hoverIndex.value = newVal.length > 0 ? 0 : -1;
  scrollToHover();
});

// 键盘操作
function onKeydown(e) {
  if (!showSuggestions.value || suggestions.value.length === 0) return;

  if (e.key === "ArrowDown") {
    hoverIndex.value = (hoverIndex.value + 1) % suggestions.value.length;
    scrollToHover();
    e.preventDefault();
  } else if (e.key === "ArrowUp") {
    hoverIndex.value =
      (hoverIndex.value - 1 + suggestions.value.length) %
      suggestions.value.length;
    scrollToHover();
    e.preventDefault();
  } else if (e.key === "Enter") {
    if (hoverIndex.value >= 0) {
      selectSuggestion(suggestions.value[hoverIndex.value]);
    } else {
      emitSearch();
    }
    e.preventDefault();
  }
}

// 滚动到当前高亮项
function scrollToHover() {
  nextTick(() => {
    const box = suggestionBox.value;
    const item = box?.querySelector('[ref="hoveredItem"]');
    if (box && item) {
      const offsetTop = item.offsetTop;
      const offsetBottom = offsetTop + item.offsetHeight;
      if (offsetTop < box.scrollTop) {
        box.scrollTop = offsetTop;
      } else if (offsetBottom > box.scrollTop + box.clientHeight) {
        box.scrollTop = offsetBottom - box.clientHeight;
      }
    }
  });
}

// 获取用户信息
onMounted(async () => {
  try {
    const res = await getProfile();
    user.value = res.data.data;
  } catch {
    user.value = null;
  }
});
</script>

<style scoped>
.card-focused {
  background-color: rgb(var(--mdui-color-surface-container-lowest)) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
}
</style>
