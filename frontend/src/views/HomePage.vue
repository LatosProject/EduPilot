<template>
  <!-- 页面整体横向布局 -->
  <div style="display: flex; height: 100vh">
    <!-- 左侧导航栏 -->
    <NavigationRail @menu-click="onMenuClick" />

    <!-- 右侧内容区域 -->
    <div
      :style="{
        flexGrow: 1,
        display: 'flex',
        paddingLeft: contentPaddingLeft + 'px',
        paddingTop: '22px',
        paddingBottom: '24px',
        transition: isInitial ? 'none' : 'padding-left 0.3s',
      }"
    >
      <!-- 左侧固定宽度区域 -->
      <div
        class="left-panel"
        :class="{ 'full-width': windowWidth <= 1000 }"
        style="min-width: 480px"
      >
        <!-- 顶部 Logo + 搜索框 -->
        <div style="display: flex; align-items: center; width: 100%">
          <!-- 左侧 Logo 区域（点击刷新首页） -->
          <div
            style="display: flex; align-items: center; cursor: pointer"
            @click="refreshHome"
          >
            <img
              src="@/assets/logo.png"
              alt="logo"
              style="width: 32px; height: 32px"
            />
            <span
              style="
                font-size: 21px;
                font-weight: 400;
                color: rgb(var(--mdui-color-primary));
                margin-left: 8px;
                margin-top: 6px;
              "
            >
              EduPilot
            </span>
          </div>

          <!-- 占位弹性空间，用于左右分开 -->
          <div style="flex: 1"></div>

          <!-- 右侧搜索框 -->
          <SearchCard
            v-if="windowWidth > 1000"
            @search="onSearchSelect"
            :filter-status="currentStatus"
            style="
              position: absolute;
              width: 720px;
              margin-right: 80px;
              height: 48px;
              margin-left: 185px;
              margin-top: 4px;
            "
          />
          <!-- 小屏搜索按钮 -->
          <div
            v-else
            style="
              display: flex;
              align-items: center;
              margin-left: auto;
              margin-right: 16px;
              transform: translateY(4px);
            "
          >
            <mdui-button-icon
              icon="search--outlined"
              @click="showMobileSearch = true"
            />
          </div>

          <!-- 用户头像 -->
          <template v-if="user && user.avatar_url">
            <mdui-button-icon
              v-if="showAvatar"
              ref="avatarRef"
              style="position: absolute; right: 24px; margin-bottom: -4px"
              @click.stop="onAvatarClick"
            >
              <img
                :src="user.avatar_url"
                style="
                  width: 40px;
                  height: 40px;
                  object-fit: cover;
                  border-radius: 50%;
                "
                alt="avatar"
              />
            </mdui-button-icon>
            <Teleport to="body" v-if="showAvatar">
              <div
                class="profile-popover"
                :style="popoverStyle"
                ref="popoverRef"
                v-show="visible"
                @click.stop
              >
                <div
                  class="user-gmail"
                  style="
                    font-size: var(--mdui-typescale-title-small-size);
                    line-height: var(--mdui-typescale-title-small-height);
                    font-weight: var(--mdui-typescal-title-small-weight);
                  "
                >
                  {{ user.email }}
                </div>

                <div class="popover-avatar">
                  <img
                    :src="user.avatar_url"
                    alt="avatar"
                    class="popover-avatar-img"
                  />
                </div>
                <div
                  class="user-welcome"
                  style="
                    font-size: var(--mdui-typescale-title-large-size);
                    line-height: var(--mdui-typescale-title-large-height);
                    font-weight: var(--mdui-typescal-title-large-weight);
                  "
                >
                  {{ user.username }}, 您好!
                </div>
                <div class="popover-btn">
                  <mdui-button
                    variant="outlined"
                    @click="router.push('/settings')"
                  >
                    设置您的 EduPilot账户
                  </mdui-button>
                </div>
                <div class="popover-btn">
                  <mdui-button
                    @click="logout"
                    variant="filled"
                    style="
                      color: rgb(var(--mdui-color-primary-light));
                      background-color: transparent;
                    "
                  >
                    退出登录
                  </mdui-button>
                </div>
              </div>
            </Teleport>
            <Teleport v-if="windowWidth < 1000" to="body">
              <div
                v-show="showMobileSearch"
                class="mobile-search-mask"
                @click="showMobileSearch = false"
              >
                <div class="mobile-search-wrapper" @click.stop>
                  <SearchCard
                    @search="onSearchSelect"
                    :filter-status="currentStatus"
                  />
                </div>
              </div>
            </Teleport>
          </template>
          <template v-else>
            <mdui-button-icon
              icon="account_circle"
              style="margin-left: auto; margin-right: 8px"
            ></mdui-button-icon>
          </template>
        </div>
        <!-- 搜索框下方按钮组，绑定筛选事件 -->
        <TaskButtonGroup
          style="margin-bottom: 16px; margin-top: 28px"
          @status-change="onStatusChange"
        />

        <!-- 列表区域 -->
        <div style="position: relative">
          <!-- 阴影，滚动时显示 -->
          <div class="top-shadow" v-show="showTopShadow"></div>

          <OverlayScrollbarsComponent
            ref="scrollbarRef"
            :options="options"
            style="height: calc(100vh - 144px); width: 100%"
          >
            <!-- 显示作业列表或空状态 -->
            <div v-if="assignments.length > 0">
              <div style="margin-left: 4px; margin-right: 4px; margin-top: 4px">
                <AssignmentCard
                  style="margin-bottom: 16px"
                  v-for="assignment in assignments"
                  :key="assignment.uuid"
                  :id="`assignment-${assignment.uuid}`"
                  :title="assignment.title"
                  @click="goDetail(assignment.uuid)"
                  :deadline="formatDeadline(assignment.deadline)"
                  :description="assignment.description"
                  :selected="assignment.uuid === selectedId"
                />
              </div>
            </div>

            <!-- 空状态提示 -->
            <div
              v-else
              style="
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
              "
            >
              尚无作业
            </div>
          </OverlayScrollbarsComponent>
        </div>
      </div>

      <!-- 主体内容卡片容器 -->
      <div
        style="
          position: relative;
          min-width: 480px;
          flex-grow: 1;
          margin-left: 16px;
          margin-top: 64px;
          margin-right: 24px;
          background-color: rgb(var(--mdui-color-surface-container-lowest));
          box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
          border-radius: var(--mdui-shape-corner-extra-large);
        "
        class="right-panel"
        v-if="windowWidth > 1000"
      >
        <!-- 顶部工具栏 -->
        <div
          v-if="currentAssignment && showHeaderAndFooter"
          style="display: flex; align-items: center; height: 56px"
        >
          <div
            style="
              margin-left: auto;
              display: flex;
              gap: 8px;
              align-items: center;
            "
          >
            <mdui-button-icon
              v-if="currentAssignment"
              icon="phonelink--outlined"
              @click="openShareQRDialog"
            ></mdui-button-icon>
            <mdui-button-icon
              v-if="currentAssignment"
              icon="question_answer--outlined"
            ></mdui-button-icon>
            <mdui-button-icon
              style="margin-right: 16px"
              icon="dark_mode--outlined"
              @click="toggleTheme"
            ></mdui-button-icon>
          </div>
        </div>

        <!-- 空状态动画 -->
        <div
          v-if="!currentAssignment"
          style="
            height: calc(100vh - 168px);
            display: flex;
            align-items: center;
            justify-content: center;
          "
        >
          <LottieAnimation
            :animation-data="animationData"
            :loop="true"
            :autoplay="true"
            :width="250"
            :height="250"
          />
        </div>

        <!-- 内容滚动区域 -->
        <OverlayScrollbarsComponent
          :options="options"
          v-if="currentAssignment && isDynamicPageRef"
          style="height: calc(100vh - 230px); width: 100%"
        >
          <div class="mdui-prose" style="margin-left: 32px; margin-top: 8px">
            <div v-if="currentAssignment && showHeaderAndFooter">
              <h1>{{ currentAssignment.title }}</h1>
              <h3>
                <small
                  ><mdui-icon-date-range
                    style="position: relative; top: 5px"
                  ></mdui-icon-date-range>
                  创建日期 {{ formatDeadline(currentAssignment.created_at) }}
                  <mdui-icon-supervisor-account
                    style="position: relative; top: 5px"
                  ></mdui-icon-supervisor-account>
                  创建人 {{ currentAssignment.created_by }}
                  <mdui-icon-grade
                    style="position: relative; top: 5px"
                  ></mdui-icon-grade>
                  满分 {{ currentAssignment.max_score }}
                  <mdui-icon-access-alarm
                    style="position: relative; top: 5px"
                  ></mdui-icon-access-alarm>
                  截止日期 {{ formatDeadline(currentAssignment.deadline) }}
                </small>
              </h3>
            </div>
            <!-- 动态渲染作业内容 -->
            <template v-if="isDynamicPageRef">
              <component
                v-for="(block, i) in parsedContent"
                :key="i"
                :is="resolveBlock(block.type)"
                :data="block"
              />
            </template>
          </div>
        </OverlayScrollbarsComponent>
        <!-- 如果是 Card 组件 -->
        <div v-if="!showHeaderAndFooter">
          <!-- 顶部工具栏 -->
          <div style="display: flex; align-items: center; height: 56px">
            <!-- 上传按钮，调用 AttachmentUploader 内部方法 -->
            <mdui-button-icon
              style="margin-left: 16px"
              icon="arrow_back"
              @click="goBackFromSubmission"
            />
            <div
              style="
                margin-left: auto;
                display: flex;
                gap: 8px;
                align-items: center;
              "
            >
              <mdui-button-icon
                v-if="files.length > 0"
                @click="openUploadDialog"
                icon="attach_file"
              />
              <mdui-button-icon icon="upload_file" @click="pickAttachment" />
              <mdui-button-icon
                style="margin-right: 16px"
                icon="dark_mode--outlined"
                @click="toggleTheme"
              />
            </div>
          </div>
          <!-- 上传对话框 -->
          <AttachmentUploader ref="uploaderRef" v-model="files" />
          <mdui-dialog
            :open="uploadDialogOpen"
            @close="uploadDialogOpen = false"
            close-on-overlay-click
            close-on-esc
          >
            <div style="max-width: 320px; overflow: hidden" id="picker">
              <!-- 附件列表 -->
              <mdui-list>
                <mdui-list-subheader>上传列表</mdui-list-subheader>
                <mdui-list-item
                  v-for="(file, i) in files"
                  :key="file.name + '_' + file.size"
                  nonclickable
                >
                  {{ file.name }}
                  <mdui-icon slot="icon" name="attach_file"></mdui-icon>
                  <!-- 删除按钮 -->
                  <mdui-button-icon
                    slot="end-icon"
                    icon="close"
                    @click="removeFile(i)"
                    class="mdui-text-color-red"
                  />
                </mdui-list-item>
              </mdui-list>
            </div>
          </mdui-dialog>

          <div class="mdui-prose" style="margin-left: 32px; margin-top: 8px">
            <h1>提交作业</h1>
          </div>
          <div
            style="
              margin-top: 52px;
              margin-left: 24px;
              margin-right: 16px;
              margin-bottom: 64px;
            "
          >
            <OverlayScrollbarsComponent
              style="height: calc(100vh - 230px); width: 100%"
              :options="options"
            >
              <SubmissionCard
                ref="submissionRef"
                v-model="submission"
                @submit="handleSubmit"
                style="padding-left: 8px; padding-top: 8px"
              />
            </OverlayScrollbarsComponent>
          </div>
          <div
            style="
              position: absolute;
              bottom: 16px;
              right: 16px;
              display: flex;
              gap: 8px;
              z-index: 50;
            "
          >
            <mdui-button
              @click="submissionRef?.onSubmit()"
              variant="filled"
              end-icon="cloud_upload"
            >
              提交
            </mdui-button>
          </div>
        </div>

        <!-- 底部操作按钮 -->
        <!-- 底部操作按钮，固定在右下 -->
        <div
          v-if="
            currentAssignment &&
            showHeaderAndFooter &&
            !currentAssignment.submitted &&
            currentStatus !== 'done' &&
            currentStatus !== '' &&
            (new Date(currentAssignment.deadline).getTime() >= Date.now() ||
              currentAssignment.allow_late_submission)
          "
          style="
            position: absolute;
            bottom: 16px;
            right: 16px;
            display: flex;
            gap: 8px;
            z-index: 50;
          "
        >
          <mdui-button
            class="on-surface-variant"
            variant="outlined"
            icon="delete"
          >
            忽略
          </mdui-button>
          <mdui-button
            @click="enterSubmissionMode"
            variant="filled"
            end-icon="arrow_forward"
          >
            提交
          </mdui-button>
        </div>

        <!-- 分享二维码弹窗 -->
        <mdui-dialog
          ref="shareQRDialog"
          class="shareQRDialog"
          close-on-overlay-click
          close-on-esc
        >
          <div
            style="
              max-width: 320px;
              max-height: 320px;
              overflow: hidden;
              border-radius: 16px;
            "
          >
            <vue-qr
              :text="currentUrl"
              :size="320"
              style="border-radius: 16px"
            />
          </div>
        </mdui-dialog>
      </div>
    </div>
    <mdui-snackbar class="upload_snackbar"></mdui-snackbar>
  </div>
</template>

<script setup>
import "@mdui/icons/search.js";
import "@mdui/icons/supervisor-account.js";
import "@mdui/icons/grade.js";
import "@mdui/icons/date-range.js";
import "@mdui/icons/access-alarm.js";
import "mdui/components/list.js";
import "mdui/components/list-item.js";
import "mdui/components/list-subheader.js";
import NavigationRail from "../components/common/NavigationRail.vue";
import SearchCard from "../components/common/SearchCard.vue";
import TaskButtonGroup from "../components/common/TaskButtonGroup.vue";
import AssignmentCard from "../components/itmes/AssignmentCard.vue";
import {
  ref,
  computed,
  onMounted,
  onUnmounted,
  onBeforeUnmount,
  watch,
  nextTick,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAssignments } from "../composables/useAssignments";
import { OverlayScrollbarsComponent } from "overlayscrollbars-vue";
import "overlayscrollbars/styles/overlayscrollbars.css";
import { formatDeadline } from "../utils/date";
import { setTheme } from "mdui/functions/setTheme.js";
import { getTheme } from "mdui/functions/getTheme.js";
import { useGlobalStore } from "../stores/global";
import { getAssignments } from "../api/assignment";
import { getClass } from "../api/classes";
import animationData from "../assets/empty.json";
import vueQr from "vue-qr/src/packages/vue-qr.vue";
import TextBlock from "@/components/blocks/TextBlock.vue";
import ListBlock from "@/components/blocks/ListBlock.vue";
import AttachmentBlock from "@/components/blocks/AttachmentBlock.vue";
import TipBlock from "@/components/blocks/TipBlock.vue";
import { getProfile, logoutApi } from "../api/auth";
import SubmissionCard from "../components/common/SubmissionCard.vue";
import AttachmentUploader from "../components/common/AttachmentUploader.vue";
import { submitAssignment } from "../api/submission";

// --- 状态定义 ---
const globalStore = useGlobalStore();
const route = useRoute();
const router = useRouter();
const classUuids = ref([]); // 【核心】在此处统一定义班级列表

// 【核心修复】必须在 setup 顶层调用，传入 ref。内部会自动 watch classUuids
const {
  assignments,
  selectedId,
  currentStatus,
  currentAssignment,
  fetchAssignments,
  selectAssignment,
} = useAssignments(classUuids);

// UI 状态
const visible = ref(false);
const popoverStyle = ref({ top: "0px", left: "0px", position: "absolute" });
const showMobileSearch = ref(false);
const files = ref([]);
const uploaderRef = ref(null);
const showTopShadow = ref(false);
const scrollbarRef = ref(null);
const isInitial = ref(true);
const shareQRDialog = ref(null);
const windowWidth = ref(window.innerWidth);
const user = ref(null);
const showHeaderAndFooter = ref(true);
const uploadDialogOpen = ref(false);
const submissionRef = ref(null);
const isDynamicPageRef = ref(true);
const submission = ref({ content: "", attachments: [] });

const avatarRef = ref(null);
const popoverRef = ref(null);
let intervalId = null;

const options = ref({
  scrollbars: { autoHide: "leave", autoHideDelay: 500 },
});

// --- 逻辑函数 ---

function updateWidth() {
  windowWidth.value = window.innerWidth;
}
const showAvatar = computed(() => windowWidth.value > 1000);

function onAvatarClick() {
  visible.value = !visible.value;
  nextTick(updatePopoverPosition);
}

const onClickOutside = (e) => {
  if (
    visible.value &&
    popoverRef.value &&
    !popoverRef.value.contains(e.target) &&
    avatarRef.value &&
    !avatarRef.value.contains(e.target)
  ) {
    visible.value = false;
  }
};

function removeFile(index) {
  files.value = files.value.filter((_, idx) => idx !== index);
  if (files.value.length === 0) uploadDialogOpen.value = false;
}

function goBackFromSubmission() {
  showHeaderAndFooter.value = true;
  isDynamicPageRef.value = true;
  uploaderRef.value?.clear?.();
  submissionRef.value?.clearAttachments?.();
  files.value = [];
}

async function handleSubmit(payload) {
  const assignmentId = currentAssignment.value?.uuid;
  const classUuid = currentAssignment.value?.class_uuid;
  if (!assignmentId || !classUuid) return;

  if (!payload.content?.trim()) {
    const snackbar = document.querySelector(".upload_snackbar");
    snackbar.textContent = "提交内容不能为空";
    snackbar.open = true;
    return;
  }

  try {
    await submitAssignment(
      classUuid,
      assignmentId,
      payload.content,
      payload.attachments || []
    );
    goBackFromSubmission();
    if (currentAssignment.value) currentAssignment.value.submitted = true;
    fetchAssignments(currentStatus.value);
    const snackbar = document.querySelector(".upload_snackbar");
    snackbar.textContent = "提交成功";
    snackbar.open = true;
  } catch (e) {
    console.error("提交失败", e);
  }
}

const parsedContent = computed(() => {
  if (!currentAssignment.value?.content) return [];
  try {
    return JSON.parse(currentAssignment.value.content);
  } catch (e) {
    return [];
  }
});

const currentUrl = computed(
  () => window.location.origin + "/assignment/" + selectedId.value
);

function refreshHome() {
  window.location.href = "/";
}

function onSearchSelect(item) {
  showMobileSearch.value = false;
  router.push({ name: "AssignmentDetail", params: { id: item.uuid } });
}

const toggle = ref(localStorage.getItem("navToggle") === "1");
const contentPaddingLeft = ref(toggle.value ? 48 : 8);

function onMenuClick() {
  toggle.value = !toggle.value;
  localStorage.setItem("navToggle", toggle.value ? "1" : "0");
  contentPaddingLeft.value = toggle.value ? 48 : 8;
}

function onScroll() {
  const osInstance = scrollbarRef.value?.osInstance();
  showTopShadow.value = (osInstance?.elements().viewport.scrollTop || 0) > 0;
}

function resolveBlock(type) {
  const map = {
    text: TextBlock,
    list: ListBlock,
    attachment: AttachmentBlock,
    tip: TipBlock,
  };
  return map[type] || TextBlock;
}

function logout() {
  localStorage.removeItem("access_token");
  router.replace({ name: "Login" });
  logoutApi();
}

function updatePopoverPosition() {
  if (!avatarRef.value || !visible.value) return;
  const rect = avatarRef.value.getBoundingClientRect();
  popoverStyle.value = {
    top: rect.bottom + window.scrollY + 12 + "px",
    left: rect.left + window.scrollX - 360 + "px",
    position: "absolute",
  };
}

// --- 生命周期 ---

onMounted(async () => {
  // 1. 初始化事件监听
  window.addEventListener("resize", updateWidth);
  window.addEventListener("resize", updatePopoverPosition);
  window.addEventListener("scroll", updatePopoverPosition, true);
  document.addEventListener("click", onClickOutside);
  isInitial.value = false;

  // 2. 获取用户信息
  getProfile()
    .then((res) => (user.value = res.data.data))
    .catch(() => (user.value = null));

  // 3. 获取班级列表并触发数据流
  try {
    const res = await getClass();
    const list = res?.items?.map((i) => i.class_uuid).filter(Boolean) ?? [];
    classUuids.value = list; // 这一步会触发 useAssignments 内部的获取作业逻辑
    globalStore.setClassUuids(list);
  } catch (e) {
    console.error("初始化班级失败", e);
  }

  // 4. 初始化滚动条监听
  nextTick(() => {
    const osInstance = scrollbarRef.value?.osInstance();
    osInstance?.elements().viewport.addEventListener("scroll", onScroll);
  });

  // 5. 轮询更新徽章
  intervalId = setInterval(async () => {
    if (classUuids.value.length > 0) {
      // 简单刷新当前列表
      fetchAssignments(currentStatus.value);
    }
  }, 60000);
});

onBeforeUnmount(() => {
  const osInstance = scrollbarRef.value?.osInstance();
  osInstance?.elements().viewport.removeEventListener("scroll", onScroll);
  clearInterval(intervalId);
});

onUnmounted(() => {
  window.removeEventListener("resize", updateWidth);
  window.removeEventListener("resize", updatePopoverPosition);
  window.removeEventListener("scroll", updatePopoverPosition, true);
  document.removeEventListener("click", onClickOutside);
});
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

.left-panel {
  flex-grow: 0;
  transition: flex-grow 0.3s;
  min-width: 480px;
}

.left-panel.full-width {
  flex-grow: 1;
  /* 当窗口小于1000px时，撑满 */
  min-width: 0;
  /* 避免 min-width 限制动画 */
  padding-right: 16px;
}

.right-panel {
  flex-grow: 1;
}

header {
  position: relative;
  padding: 16px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
}

.profile-popover {
  position: absolute;
  /* 必须有 */
  width: 400px;
  background: rgb(var(--mdui-color-surface-container-high));
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  z-index: 1000;
}

.item {
  padding: 10px 16px;
  cursor: pointer;
}

.item:hover {
  background: #f5f5f5;
}

.divider {
  height: 1px;
  background: #eee;
  margin: 6px 0;
}

.danger {
  color: #d93025;
}

.profile-popover .user-gmail {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 12px 12px;
  text-align: center;
}

.profile-popover .user-welcome {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 4px;
  padding-bottom: 2px;
  padding-left: 12px;
  padding-right: 12px;
  text-align: center;
}

.popover-btn {
  display: flex;
  justify-content: center;
  padding: 8px 16px;
}

.popover-avatar {
  display: flex;
  justify-content: center;
  padding: 12px 0 4px;
}

.popover-avatar-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.mobile-search-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.32);
  z-index: 3000;

  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.mobile-search-wrapper {
  width: 100%;
  max-width: 1000px;
  margin-top: 18px;
  padding: 0 16px;
}
</style>
