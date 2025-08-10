<template>
  <!-- 页面整体横向布局 -->
  <div style="display: flex; height: 100vh;">
    <!-- 左侧导航栏 -->
    <NavigationRail />
    <!-- 右侧内容区域 -->
    <div style="flex-grow: 1; display: flex; padding-left: 8px; padding-top: 24px;">
      <!-- 左侧固定宽度区域 -->
      <div style="width: 480px;">
        <!-- 顶部搜索卡片 -->
        <SearchCard />
        <!-- 搜索框下方按钮组，绑定筛选事件 -->
        <TaskButtonGroup @status-change="onStatusChange" />
        <OverlayScrollbarsComponent :options="options" style="height: 100%; width: 100%;margin-top: 16px">
          <div style="margin-left: 4px;margin-right: 4px ;margin-top: 4px">
            <AssignmentCard style="margin-bottom: 16px;" v-for="assignment in assignments" :key="assignment.uuid"
              :title="assignment.title" @click="goDetail(assignment.uuid)"
              :deadline="formatDeadline(assignment.deadline)" :content="assignment.content"
              :selected="assignment.uuid !== selectedId" />
          </div>
        </OverlayScrollbarsComponent>
      </div>
      <!-- 主体内容卡片容器 -->
      <div style="
          flex-grow: 1;
          margin-left: 16px;
          margin-right: 24px;
          background-color: rgb(var(--mdui-color-surface-container-lowest));
          box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.20);
          border-radius: var(--mdui-shape-corner-extra-large);
        ">
        <!-- 内容 -->
        <p v-if="currentAssignment">{{ currentAssignment.title }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import NavigationRail from '../components/common/NavigationRail.vue'
import SearchCard from '../components/common/SearchCard.vue'
import TaskButtonGroup from '../components/common/TaskButtonGroup.vue'
import AssignmentCard from '../components/itmes/AssignmentCard.vue'
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAssignments } from '../composables/useAssignments'
import { OverlayScrollbarsComponent } from 'overlayscrollbars-vue'
import 'overlayscrollbars/styles/overlayscrollbars.css'
import { formatDeadline } from '../utils/date'
const classUuid = 'e0453e99-a7e4-43fa-a480-5272add34867'

const { assignments, selectedId, currentStatus, currentAssignment, fetchAssignments } = useAssignments(classUuid)

const route = useRoute()
const router = useRouter()

const options = ref({
  scrollbars: {
    autoHide: 'leave',
    autoHideDelay: 500,
  },
})

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
  fetchAssignments(currentStatus.value)
  intervalId = setInterval(() => {
    fetchAssignments(currentStatus.value)
  }, 60000)
})

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
