<template>
  <mdui-navigation-rail ref="railRef" style="padding-top: 8px" contained>
    <!-- 菜单按钮 -->
    <mdui-button-icon
      @click="
        $emit('menu-click');
        toggle = !toggle;
        saveToggle();
      "
      slot="top"
      :icon="toggle ? 'menu_open' : 'menu'"
    ></mdui-button-icon>

    <!-- 占位 FAB -->
    <mdui-fab class="fab-fake"></mdui-fab>

    <!-- 可扩展 FAB -->
    <mdui-fab
      class="fab-purple fab-extend"
      lowered
      icon="edit--rounded"
      :extended="toggle"
      slot="top"
    >
      编辑
    </mdui-fab>

    <!-- 导航项 -->
    <mdui-navigation-rail-item
      v-for="item in navItems"
      :key="item.path"
      :class="[
        'label-medium secondary',
        { 'custom-toggle-style': toggle, 'toggle-active': toggle,'.custom-toggle-style':toggle },
      ]"
      :icon="item.icon"
      :value="item.value"
      @click="go(item)"
    >
      <span class="item-label">{{ item.label }}</span>
    </mdui-navigation-rail-item>
  </mdui-navigation-rail>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";
import { onMounted, watch, ref } from "vue";

const router = useRouter();
const route = useRoute();
const railRef = ref(null);
const savedToggle = localStorage.getItem("navToggle");
const toggle = ref(savedToggle === "1"); // 初始化读取 localStorage

const navItems = [
  { label: "主页", path: "/", icon: "inbox--rounded", value: "home" },
  { label: "学习", path: "/study", icon: "book--rounded", value: "study" },
  { label: "设置", path: "/settings", icon: "settings--rounded", value: "setting" },
];

// 点击跳转
function go(item) {
  router.push(item.path);
}

// 路由同步选中状态
function syncActiveValue(path) {
  const found = navItems.find((i) => i.path === path);
  if (railRef.value) {
    railRef.value.value = found ? found.value : "home";
  }
}

onMounted(() => {
  syncActiveValue(route.path);
});

// 监听路由变化
watch(
  () => route.path,
  (newPath) => {
    syncActiveValue(newPath);
  
  }
);

// --- 保存 toggle 状态到 localStorage ---
function saveToggle() {
  localStorage.setItem("navToggle", toggle.value ? "1" : "0");
  console.log("Saved toggle:", toggle.value);
}
</script>

<style scoped>
/* FAB 占位 */
.fab-fake {
  opacity: 0;
  pointer-events: none;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  transition: width 0.3s ease;
}

/* 可扩展 FAB */
.fab-extend {
  position: absolute;
  top: 60px;
  left: 12px;
}

.fab-extend.expanded {
  width: 160px;
}

/* 导航文字样式 */
::v-deep(.custom-toggle-style) {
  height: 3.5rem;
  position: relative;
}

::v-deep(.custom-toggle-style .item-label) {
  position: absolute;
  left: 56px;
  top: 46%;
  transform: translate3d(-20px, -50%, 0);
  opacity: 0;
  white-space: nowrap;
  font-size: 14px;
  z-index: 1;
  transition: transform 0.36s cubic-bezier(.2, .9, .2, 1), opacity 0.28s ease;
}

::v-deep(.custom-toggle-style.toggle-active .item-label) {
  transform: translate3d(0, -50%, 0);
  opacity: 1;
}

/* 导航指示器 */
::v-deep(mdui-navigation-rail-item.custom-toggle-style)::part(indicator) {
  position: absolute;
  top: 0;
  left: 0;
  width: 6.3rem;
  height: 3.3rem;
  border-radius: 32px;
  transition: all 0.3s ease;
}

::v-deep(mdui-navigation-rail-item.custom-toggle-style:hover)::part(indicator) {
  width: 6.3rem;
  height: 3.3rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

::v-deep(mdui-navigation-rail-item.custom-toggle-style)::part(icon) {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1;
}

::v-deep(.custom-toggle-style mdui-badge) {
  position: absolute;
  top: 18px;
  right: 20px;
  z-index: 2;
}

::v-deep(.badge-absolute) {
  position: absolute;
  top: 12px;
  left: 48px;
}

::v-deep(.custom-toggle-style) {
  --mdui-comp-ripple-state-layer-color: transparent !important;
}


::v-deep(.custom-toggle-style .label-wrapper) {
  position: absolute;
  left: 56px;
  top: 50%;
  transform: translateY(-50%);
  overflow: hidden;
  height: 1.2rem;
}
</style>
