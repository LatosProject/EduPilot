<template>
  <!-- 页面整体居中布局 -->
  <div
    style="
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    "
  >
    <!-- 弹窗容器 -->
    <div
      style="
        position: relative;
        width: 480px;
        min-height: 320px;
        background-color: rgb(var(--mdui-color-surface-container-lowest));
        box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
        border-radius: var(--mdui-shape-corner-extra-large);
        padding: 24px;
        overflow: hidden;
      "
    >
      <!-- 主标题 -->
      <span
        style="
          font-family: 'Noto Sans SC';
          font-size: 32px;
          margin-top: 16px;
          display: block;
        "
      >
        班级
      </span>

      <!-- 副标题 -->
      <span
        style="
          font-family: 'Noto Sans SC';
          font-size: 16px;
          margin-top: 14px;
          margin-bottom: 24px;
          display: block;
          color: var(--mdui-color-text-secondary);
        "
      >
        您当前未进入任何班级
      </span>

      <!-- 邀请码输入框 -->
      <mdui-text-field
        ref="invitecodeField"
        v-model="inviteCode"
        variant="outlined"
        label="邀请码"
        style="margin-top: 12px; width: 100%;"
      />

      <!-- 左下角：退出登录按钮 -->
      <div
        style="
          position: absolute;
          left: 8px;
          bottom: 18px;
          color: rgb(var(--mdui-color-primary-light));
          background-color: transparent;
        "
      >
        <mdui-button
          type="button"
          style="color: rgb(var(--mdui-color-primary-light)); background-color: transparent;"
          @click="logout"
        >
          退出登录
        </mdui-button>
      </div>

      <!-- 右下角：加入班级按钮 -->
      <div style="position: absolute; right: 18px; bottom: 18px;">
        <mdui-button type="submit" @click="handleJoin">
          加入
        </mdui-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from 'vue-router';
import { joinClass } from "../api/classes";
import { logoutApi } from '../api/auth';
import { useGlobalStore } from '../stores/global';

// 全局状态管理
const globalStore = useGlobalStore();

// 路由对象
const router = useRouter();

// 邀请码输入框 ref
const invitecodeField = ref(null);

// 输入的邀请码
const inviteCode = ref("");

// 加入班级逻辑
const handleJoin = async () => {
  // 校验输入是否为空
  if (!inviteCode.value) {
    invitecodeField.value?.setCustomValidity('邀请码不能为空');
    invitecodeField.value?.reportValidity();
    return;
  }

  // 清除自定义校验信息
  invitecodeField.value?.setCustomValidity('');
  invitecodeField.value?.reportValidity();

  try {
    // 调用 API 加入班级
    const res = await joinClass(inviteCode.value);
    const classUuid = res.data.data.class_uuid;

    // 更新全局班级列表
    globalStore.setClassUuids([...globalStore.classUuids, classUuid]);

    // 跳转到首页
    router.push({ name: 'Home' });
  } catch (err) {
    // 显示 API 返回的错误信息
    if (err.response?.data?.message) {
      invitecodeField.value?.setCustomValidity(err.response.data.message);
      invitecodeField.value?.reportValidity();
    }
  }
};

// 退出登录逻辑
function logout() {
  logoutApi();
  localStorage.removeItem('access_token');
  router.push('/login');
}

// 页面挂载时判断是否已进入班级
onMounted(async () => {
  const token = localStorage.getItem('access_token');

  if (globalStore.classUuids.length && token !== null) {
    // 已加入班级，跳转首页
    router.replace({ name: 'Home' });
    return;
  } else if (!globalStore.classUuids.length && token !== null) {
    // 未加入班级，停留在邀请页
    router.replace({ name: 'Invite' });
    return;
  }
});
</script>
