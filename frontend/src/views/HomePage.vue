<template>
  <!-- 页面整体横向布局 -->
  <div style="display: flex; height: 100vh;">

    <!-- 左侧导航栏 -->
    <NavigationRail @menu-click="onMenuClick" />

    <!-- 右侧内容区域 -->
    <div :style="{
      flexGrow: 1,
      display: 'flex',
      paddingLeft: contentPaddingLeft + 'px',
      paddingTop: '22px',
      paddingBottom: '24px',
      transition: isInitial ? 'none' : 'padding-left 0.3s'
    }">

      <!-- 左侧固定宽度区域 -->
      <div style="width: 480px; min-width: 480px;">

        <!-- 顶部 Logo + 搜索框 -->
        <div style="display: flex; align-items: center; width: 100%;">

          <!-- 左侧 Logo 区域（点击刷新首页） -->
          <div style="display: flex; align-items: center; cursor: pointer;" @click="refreshHome">
            <img src="@/assets/logo.png" alt="logo" style="width: 32px; height: 32px;" />
            <span style="
              font-size: 21px;
              font-weight: 400;
              color: rgb(var(--mdui-color-primary));
              margin-left: 8px;
              margin-top: 6px;
            ">
              EduPilot
            </span>
          </div>

          <!-- 占位弹性空间，用于左右分开 -->
          <div style="flex: 1;"></div>

          <!-- 右侧搜索框 -->
          <SearchCard @search="onSearchSelect" :filter-status="currentStatus"
            style="position: absolute; width: 720px; margin-right: 80px; height: 48px; margin-left: 185px; margin-top: 4px;" />
        </div>

        <!-- 搜索框下方按钮组，绑定筛选事件 -->
        <TaskButtonGroup style="margin-bottom: 16px; margin-top:28px;" @status-change="onStatusChange" />

        <!-- 列表区域 -->
        <div style="position: relative;">
          <!-- 阴影，滚动时显示 -->
          <div class="top-shadow" v-show="showTopShadow"></div>

          <OverlayScrollbarsComponent ref="scrollbarRef" :options="options"
            style="height: calc(100vh - 144px); width: 100%;">
            <!-- 显示作业列表或空状态 -->
            <div v-if="assignments.length > 0">
              <div style="margin-left: 4px; margin-right: 4px; margin-top: 4px;">
                <AssignmentCard style="margin-bottom: 16px" v-for="assignment in assignments" :key="assignment.uuid"
                  :id="`assignment-${assignment.uuid}`" :title="assignment.title" @click="goDetail(assignment.uuid)"
                  :deadline="formatDeadline(assignment.deadline)" :description="assignment.description"
                  :selected="assignment.uuid === selectedId" />
              </div>
            </div>

            <!-- 空状态提示 -->
            <div v-else style="
                height: calc(100vh - 176px);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Noto Sans SC';
                font-weight: var(--mdui-typescale-headline-small-weight);
                font-size: var(--mdui-typescale-headline-small-size);
                line-height: var(--mdui-typescale-headline-small-line-height);
                letter-spacing: var(--mdui-typescale-headline-small-tracking);
                color: var(--mdui-color-on-surface-variant);
              ">
              尚无作业
            </div>
          </OverlayScrollbarsComponent>
        </div>
      </div>

      <!-- 主体内容卡片容器 -->
      <div style="
          position: relative;
          min-width: 480px;
          flex-grow: 1;
          margin-left: 16px;
          margin-top: 64px;
          margin-right: 24px;
          background-color: rgb(var(--mdui-color-surface-container-lowest));
          box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.20);
          border-radius: var(--mdui-shape-corner-extra-large);
        ">

        <!-- 顶部工具栏 -->
        <div style="display: flex; align-items: center; height: 56px;">
          <div style="margin-left: auto; display: flex; gap: 8px; align-items: center;">
            <mdui-button-icon v-if="currentAssignment" icon="share--outlined"
              @click="openShareQRDialog"></mdui-button-icon>
            <mdui-button-icon v-if="currentAssignment" icon="question_answer--outlined"></mdui-button-icon>
            <mdui-button-icon style="margin-right: 16px" icon="dark_mode--outlined"
              @click="toggleTheme"></mdui-button-icon>
          </div>
        </div>

        <!-- 空状态动画 -->
        <div v-if="!currentAssignment"
          style="height: calc(100vh - 168px); display: flex; align-items: center; justify-content: center;">
          <LottieAnimation :animation-data="animationData" :loop="true" :autoplay="true" :width="250" :height="250" />
        </div>

        <!-- 内容滚动区域 -->
        <OverlayScrollbarsComponent :options="options" v-if="currentAssignment"
          style="height: calc(100vh - 230px); width: 100%;">
          <div class="mdui-prose" style="margin-left: 32px; margin-top: 8px;">
            <h1>{{ currentAssignment.title }}</h1>
            <h3>
              <small>
                创建日期: {{ formatDeadline(currentAssignment.created_at) }}
                创建人: {{ currentAssignment.created_by }}
              </small>
            </h3>


            <!-- 动态渲染作业内容 -->
            <component v-for="(block, i) in parsedContent" :key="i" :is="resolveBlock(block.type)" :data="block" />

          </div>
        </OverlayScrollbarsComponent>


        <!-- 底部操作按钮 -->
        <div v-if="currentAssignment" style="
            position: absolute;
            bottom: 16px;
            right: 16px;
            display: flex;
            gap: 8px;
          ">
          <mdui-button class="on-surface-variant" variant="outlined" icon="delete">
            忽略
          </mdui-button>
          <mdui-button variant="filled" end-icon="arrow_forward">
            提交
          </mdui-button>
        </div>

        <!-- 分享二维码弹窗 -->
        <mdui-dialog ref="shareQRDialog" class="shareQRDialog" close-on-overlay-click close-on-esc>
          <div style="
      max-width: 320px; 
      max-height: 320px; 
      overflow: hidden; 
      border-radius: 16px;
    ">
            <vue-qr :text="currentUrl" :size="320" style="border-radius: 16px;" />
          </div>
        </mdui-dialog>

      </div>
    </div>
  </div>
</template>

<script setup>
import NavigationRail from '../components/common/NavigationRail.vue'
import SearchCard from '../components/common/SearchCard.vue'
import TaskButtonGroup from '../components/common/TaskButtonGroup.vue'
import AssignmentCard from '../components/itmes/AssignmentCard.vue'
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssignments } from '../composables/useAssignments'
import { OverlayScrollbarsComponent } from 'overlayscrollbars-vue'
import 'overlayscrollbars/styles/overlayscrollbars.css'
import { formatDeadline } from '../utils/date'
import { setTheme } from 'mdui/functions/setTheme.js'
import { getTheme } from 'mdui/functions/getTheme.js'
import { useGlobalStore } from '../stores/global'
import { getAssignments } from '../api/assignment'
import { getClass } from '../api/classes'
import animationData from "../assets/empty.json"
import vueQr from 'vue-qr/src/packages/vue-qr.vue'
import TextBlock from "@/components/blocks/TextBlock.vue";
import ListBlock from "@/components/blocks/ListBlock.vue";
import AttachmentBlock from "@/components/blocks/AttachmentBlock.vue";
import TipBlock from "@/components/blocks/TipBlock.vue";

const globalStore = useGlobalStore()

// 作业数据及状态管理
const { assignments, selectedId, currentStatus, currentAssignment, fetchAssignments } = useAssignments(globalStore.classUuids)
const route = useRoute()
const router = useRouter()

// DOM 和 UI 控制
const showTopShadow = ref(false)
const scrollbarRef = ref(null)
const isInitial = ref(true)
const shareQRDialog = ref(null)

// props
defineProps({
  filterStatus: String
})

// 解析 content 字符串为数组
const parsedContent = computed(() => {
  if (!currentAssignment.value.content) return []
  try {
    return JSON.parse(currentAssignment.value.content)
  } catch (e) {
    console.error('解析作业内容失败', e)
    return []
  }
})

// 当前作业链接，用于生成二维码
const currentUrl = computed(() => {
  return window.location.origin + '/assignment/' + selectedId.value
})

// 跳转首页并刷新
function refreshHome() {
  window.location.href = '/'
}

// OverlayScrollbars 配置
const options = ref({
  scrollbars: { autoHide: 'leave', autoHideDelay: 500 }
})

// 搜索选择事件
function onSearchSelect(item) {
  router.push({ name: 'AssignmentDetail', params: { id: item.uuid } })
  nextTick(() => {
    const el = document.querySelector(`#assignment-${item.uuid}`)
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

// 打开二维码分享弹窗
function openShareQRDialog() {
  if (shareQRDialog.value) {
    shareQRDialog.value.open = true
  }
}

// 路由 id 变化，更新选中作业
watch(() => route.params.id, (newId) => {
  if (newId) selectedId.value = newId
})

// 导航栏折叠状态
const toggle = ref(localStorage.getItem("navToggle") === "1")
const contentPaddingLeft = ref(toggle.value ? 48 : 8)

// 导航栏折叠事件
function onMenuClick() {
  toggle.value = !toggle.value
  localStorage.setItem("navToggle", toggle.value ? "1" : "0")
  contentPaddingLeft.value = toggle.value ? 48 : 8
}

// 页面挂载后允许动画
onMounted(() => {
  isInitial.value = false
})

// 切换主题
function toggleTheme() {
  let theme = getTheme()
  if (theme === 'auto') {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    theme = prefersDark ? 'dark' : 'light'
  }

  if (theme === "dark") {
    setTheme("light")
    localStorage.setItem('theme', 'light')
  } else {
    setTheme("dark")
    localStorage.setItem('theme', 'dark')
  }
}

// 跳转作业详情
function goDetail(id) {
  selectedId.value = id
  router.push({ name: 'AssignmentDetail', params: { id } })
}

// 筛选按钮事件
function onStatusChange(filterStatus) {
  currentStatus.value = filterStatus
  fetchAssignments(filterStatus)
}

// 页面挂载初始化
let intervalId = null
onMounted(async () => {
  isInitial.value = false

  // 获取班级列表
  let res = null
  try {
    res = await getClass()
  } catch (e) {
    console.error('getClass failed', e)
  }
  const classList = res?.items?.map(i => i.class_uuid).filter(Boolean) ?? []
  globalStore.setClassUuids(classList)

  // 初始化滚动条
  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return
  osInstance.elements().viewport.addEventListener('scroll', onScroll)

  // 初次加载作业列表
  fetchAssignments(currentStatus.value)

  // 定时刷新作业列表和徽章
  intervalId = setInterval(async () => {
    try {
      let totalBadge = 0
      for (const cls of globalStore.classUuids) {
        const res = await getAssignments(cls, 1, 10, 'created_at', 'asc', 'pending')
        totalBadge += res.pagination?.total || 0
      }
      globalStore.setBadgeCount(totalBadge)

      // 刷新作业列表
      fetchAssignments(currentStatus.value)
    } catch (e) {
      console.error('刷新作业失败', e)
    }
  }, 60000)
})

// 滚动事件，显示顶部阴影
function onScroll() {
  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return
  const scrollTop = osInstance.elements().viewport.scrollTop
  showTopShadow.value = scrollTop > 0
}

// 页面卸载
onBeforeUnmount(() => {
  const osInstance = scrollbarRef.value?.osInstance()
  if (!osInstance) return
  osInstance.elements().viewport.removeEventListener('scroll', onScroll)
})

onUnmounted(() => {
  clearInterval(intervalId)
})

function resolveBlock(type) {
  return {
    text: TextBlock,
    list: ListBlock,
    attachment: AttachmentBlock,
    tip: TipBlock,
  }[type];
}

</script>

<style>
/* 顶部滚动阴影 */
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
}
</style>
