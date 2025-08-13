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
            <div style="margin-left: 4px;margin-right: 4px ;margin-top: 4px">
              <AssignmentCard style="margin-bottom: 16px;" v-for="assignment in assignments" :key="assignment.uuid"
                :title="assignment.title" @click="goDetail(assignment.uuid)"
                :deadline="formatDeadline(assignment.deadline)" :description="assignment.description"
                :selected="assignment.uuid !== selectedId" />
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
            <mdui-button-icon icon="share--outlined"></mdui-button-icon>
            <mdui-button-icon icon="question_answer--outlined"></mdui-button-icon>
            <mdui-button-icon style="margin-right:16px" icon="dark_mode--outlined"
              @click="toggleTheme"></mdui-button-icon>
          </div>
        </div>

        <!-- 内容 -->
        <OverlayScrollbarsComponent :options="options"
          style=" height:calc(100vh - 168px); width: 100%;margin-bottom: 0px">
          <div class="mdui-prose" style="margin-left: 32px; margin-top: 8px;" v-if="currentAssignment">
            <h1>{{ currentAssignment.title }}</h1>
            <h3><small>创建日期: {{ formatDeadline(currentAssignment.created_at) }} 创建人: {{ currentAssignment.created_by
                }}</small></h3>
            <p>{{ currentAssignment.content }}</p>
          </div>
        </OverlayScrollbarsComponent>
        <div style="
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
const globalStore = useGlobalStore()

globalStore.setClassUuid("e0453e99-a7e4-43fa-a480-5272add34867")

const { assignments, selectedId, currentStatus, currentAssignment, fetchAssignments } = useAssignments(globalStore.classUuid)

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
onMounted(() => {
  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return

  osInstance.elements().viewport.addEventListener('scroll', onScroll)
  fetchAssignments(currentStatus.value)
  intervalId = setInterval(async () => {
    const res = await getAssignments(globalStore.classUuid, 1, 10, 'created_at', 'asc', 'pending')
    globalStore.setBadgeCount(res.pagination.total)
    fetchAssignments(currentStatus.value)
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