<template>
  <mdui-card
    ref="cardRef"
    :class="{ 'card-focused': isEditing }"
    style="
      cursor: text;
      border-radius: var(--mdui-shape-corner-extra-large);
      height: 56px;
      display: flex;
      align-items: center;
      padding: 0;
      gap: 0;
      background-color: rgb(var(--mdui-color-surface-container-high));
      transition: all 0.2s ease;
    "
    @click="startEditing"
  >
    <!-- 搜索图标 -->
    <mdui-icon
      name="search"
      style="
        font-size: 24px;
        color: rgb(var(--mdui-color-on-surface-variant));
        user-select: none;
        margin: 0 16px;
      "
    ></mdui-icon>
    <!-- 非编辑状态 -->
    <div
      v-if="!isEditing"
      style="
        font-size: 16px;
        line-height: 56px; /* 和 Card 高度一致 */
        letter-spacing: 0.5px;
        font-weight: 400;
        font-family: 'Noto Sans SC';
        user-select: none;
        color: rgb(var(--mdui-color-on-surface-variant));
      "
    >
      {{ keyword || "搜索" }}
    </div>
    <!-- 编辑状态 -->
    <input
      v-else
      ref="searchInput"
      v-model="keyword"
      placeholder="搜索"
      style="
        flex: 1;
        font-size: 16px;
        line-height: 56px; /* 和 Card 高度一致 */
        letter-spacing: 0.5px;
        font-weight: 400;
        font-family: 'Noto Sans SC';
        color: rgb(var(--mdui-color-on-surface-variant));
        border: none;
        outline: none;
        background: transparent;
        padding: 0;
        margin: 0;
        box-sizing: border-box;
      "
      @blur="stopEditing"
    />
    <!-- 用户头像 -->
    <template v-if="user && user.avatar_url">
      <mdui-button-icon style="margin-left: auto; margin-right: 8px">
        <img
          :src="user.avatar_url"
          style="background-color: rgb(var(--mdui-color-primary-container))"
          alt="avatar"
        />
      </mdui-button-icon>
    </template>
    <template v-else>
      <mdui-button-icon
        icon="account_circle"
        style="margin-left: auto; margin-right: 8px"
      ></mdui-button-icon>
    </template>
  </mdui-card>
</template>
<script setup>
import { ref, nextTick, onMounted } from "vue";
import { getProfile } from "../../api/auth";
const user = ref(null);
const isEditing = ref(false);
const keyword = ref("");
const searchInput = ref(null);
onMounted(async () => {
  try {
    const res = await getProfile();
    user.value = res.data.data;
  } catch (error) {
    user.value = null;
  }
});
function startEditing() {
  isEditing.value = true;
  nextTick(() => searchInput.value?.focus());
}
function stopEditing() {
  isEditing.value = false;
}
</script>
<style scoped>
/* 默认状态 */
.mdui-card {
  background-color: rgb(var(--mdui-color-surface-container-high));
}

.card-focused {
  background-color: rgb(var(--mdui-color-surface-container-lowest)) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
  /* 阴影 */
}
</style>
