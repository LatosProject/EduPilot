<template>
  <!-- 页面整体横向布局 -->
  <div style="display: flex; height: 100vh;">
    <!-- 左侧导航栏 -->
    <NavigationRail />
    <!-- 右侧内容区域 -->
    <div style="flex-grow: 1; display: flex; padding-left: 8px; padding-top: 24px;padding-bottom: 24px;">
      <!-- 左侧固定宽度区域 -->
      <div style="width: 480px; min-width: 480px;">
        <!-- 顶部搜索卡片 -->
        <SearchCard />
        <!-- 搜索框下方按钮组，绑定筛选事件 -->
        <TaskButtonGroup style="margin-bottom: 16px" @status-change="onStatusChange" />
        <div style="position: relative;">
          <!-- 阴影放这里，绝对定位相对这个容器 -->
          <div class="top-shadow" v-show="showTopShadow"></div>
          <OverlayScrollbarsComponent ref="scrollbarRef" :options="options"
            style=" height:calc(100vh - 144px); width: 100%;">
            <!-- 在内部根据 assignments.length > 0 来决定显示列表或“尚无作业” -->
            <div v-if="assignments.length > 0">
              <div style="margin-left: 4px;margin-right: 4px ;margin-top: 4px">
                <AssignmentCard style="margin-bottom: 16px;" v-for="assignment in assignments" :key="assignment.uuid"
                  :title="assignment.title" @click="goDetail(assignment.uuid)"
                  :deadline="formatDeadline(assignment.deadline)" :description="assignment.description"
                  :selected="assignment.uuid !== selectedId" />
              </div>
            </div>
            <div v-else style="height: calc(100vh - 176px); display: flex; align-items: center; justify-content: center;
              font-family: 'Noto Sans SC';
              font-weight: var(--mdui-typescale-headline-small-weight);
              font-size: var(--mdui-typescale-headline-small-size);
              line-height: var(--mdui-typescale-headline-small-line-height);
              letter-spacing: var(--mdui-typescale-headline-small-tracking);
              color: var(--mdui-color-on-surface-variant);">
              尚无作业
            </div>
          </OverlayScrollbarsComponent>
        </div>
      </div>

      <!-- 主体内容卡片容器 -->
      <div style="
        min-width: 480px;
          flex-grow: 1;
          margin-left: 16px;
          margin-right: 24px;
          background-color: rgb(var(--mdui-color-surface-container-lowest));
          box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.20);
          border-radius: var(--mdui-shape-corner-extra-large);
        ">
        <div style="display: flex; align-items: center;height:56px">

          <div style="margin-left:auto; display:flex; gap:8px; align-items:center;">
            <mdui-button-icon v-if="currentAssignment" icon="share--outlined"></mdui-button-icon>
            <mdui-button-icon v-if="currentAssignment" icon="question_answer--outlined"></mdui-button-icon>
            <mdui-button-icon style="margin-right:16px" icon="dark_mode--outlined"
              @click="toggleTheme"></mdui-button-icon>
          </div>
        </div>
        <div v-if="!currentAssignment"
          style="height: calc(100vh - 168px); display: flex; align-items: center; justify-content: center;">
          <LottieAnimation :animation-data="animationData" :loop="true" :autoplay="true" :width="250" :height="250" />
        </div>
        <!-- 内容 -->
        <OverlayScrollbarsComponent :options="options" v-if="currentAssignment"
          style=" height:calc(100vh - 168px); width: 100%;margin-bottom: 0px">
          <div class="mdui-prose" style="margin-left: 32px; margin-top: 8px;" v-if="currentAssignment">
            <h1>{{ currentAssignment.title }}</h1>
            <h3><small>创建日期: {{ formatDeadline(currentAssignment.created_at) }} 创建人: {{ currentAssignment.created_by
                }}</small></h3>
            <p>{{ currentAssignment.content }}</p>
          </div>
        </OverlayScrollbarsComponent>
        <div v-if="currentAssignment" style="
          display: flex;
          justify-content: flex-end;
          align-items: flex-end;
          padding-right: 16px;
          padding-bottom: 16px;
          padding-top: 8px;
        ">
          <mdui-button class="on-surface-variant" variant="outlined" icon="delete" style="margin-right: 8px;">
            忽略
          </mdui-button>
          <mdui-button variant="filled" end-icon="arrow_forward">
            提交
          </mdui-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import NavigationRail from '../components/common/NavigationRail.vue'
import SearchCard from '../components/common/SearchCard.vue'
import TaskButtonGroup from '../components/common/TaskButtonGroup.vue'
import AssignmentCard from '../components/itmes/AssignmentCard.vue'
import { ref, onMounted, onUnmounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssignments } from '../composables/useAssignments'
import { OverlayScrollbarsComponent } from 'overlayscrollbars-vue'
import 'overlayscrollbars/styles/overlayscrollbars.css'
import { formatDeadline } from '../utils/date'
import { setTheme } from 'mdui/functions/setTheme.js';
import { getTheme } from 'mdui/functions/getTheme.js';
import { useGlobalStore } from '../stores/global'
import { getAssignments } from '../api/assignment'
import { getClass } from '../api/classes'
import animationData from "../assets/empty.json";
const globalStore = useGlobalStore()
const { assignments, selectedId, currentStatus, currentAssignment, fetchAssignments } = useAssignments(globalStore.classUuids)
const route = useRoute()
const router = useRouter()
const showTopShadow = ref(false)
const scrollbarRef = ref(null)
const options = ref({
  scrollbars: {
    autoHide: 'leave',
    autoHideDelay: 500,
  },
})
function toggleTheme() {
  let theme = getTheme();
  if (theme === 'auto') {
    // 判断实际生效的主题
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    theme = prefersDark ? 'dark' : 'light';
  }

  if (theme === "dark") {
    setTheme("light");
    localStorage.setItem('theme', 'light');
  } else {
    setTheme("dark");
    localStorage.setItem('theme', 'dark');
  }
}



// 跳转详情页并选中
function goDetail(id) {
  selectedId.value = id
  router.push({ name: 'AssignmentDetail', params: { id } })
}

// 监听筛选按钮事件，刷新作业列表
function onStatusChange(status) {
  currentStatus.value = status
  fetchAssignments(status)
}

let intervalId = null
onMounted(async () => {
let res = null
try {
  res = await getClass()
} catch(e) {
  console.error('getClass failed', e)
}
const classList = res?.items?.map(i => i.class_uuid).filter(Boolean) ?? []
globalStore.setClassUuids(classList)
// 安全判断长度
if (!globalStore.classUuids.length) {
  // 数组为空，跳转到 Invite 页面
  router.push({ name: 'Invite' })
  return
}
  // if (items.length > 0) {
  //   console.log(items)
  //   const classUuid = items[0].class_uuid
  //   globalStore.setClassUuid(classUuid)
  // } else {
  //   return
  // }


  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return

  osInstance.elements().viewport.addEventListener('scroll', onScroll)
  fetchAssignments(currentStatus.value)
  intervalId = setInterval(async () => {
    try {
      let totalBadge = 0
      for (const cls of globalStore.classUuids) {
        const res = await getAssignments(cls, 1, 10, 'created_at', 'asc', 'pending')
        totalBadge += res.pagination?.total || 0
      }
      console.log('totalBadge', totalBadge)  // <--- 打印检查
      globalStore.setBadgeCount(totalBadge)

      // 刷新作业列表
      fetchAssignments(currentStatus.value)
    } catch (e) {
      console.error('刷新作业失败', e)
    }
  }, 60000)

})
onBeforeUnmount(() => {
  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return

  osInstance.elements().viewport.removeEventListener('scroll', onScroll)
})

function onScroll() {
  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return

  const scrollTop = osInstance.elements().viewport.scrollTop
  showTopShadow.value = scrollTop > 0
}

onUnmounted(() => {
  clearInterval(intervalId)
})

// 监听路由 id 变化，更新选中
watch(
  () => route.params.id,
  (newId) => {
    if (newId) selectedId.value = newId
  }
)
</script>

<style>
.top-shadow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  pointer-events: none;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.05), transparent);
  z-index: 10;
  border-radius: 8px;
  /* 你可以调整数值，越大圆角越明显 */
}
</style>