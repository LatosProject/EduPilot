<template>
    <div style="
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    ">
        <div style="
        position: relative;
        width: 480px;
        min-height: 320px;
        background-color: rgb(var(--mdui-color-surface-container-lowest));
        box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
        border-radius: var(--mdui-shape-corner-extra-large);
        padding: 24px;
        overflow: hidden;
      ">
            <!-- 标题 -->
            <span style="
          font-family: 'Noto Sans SC';
          font-size: 32px;
          margin-top: 16px;
          display: block;
        ">
                班级
            </span>

            <!-- 副标题 -->
            <span style="
          font-family: 'Noto Sans SC';
          font-size: 16px;
          margin-top: 14px;
          margin-bottom: 24px;
          display: block;
          color: var(--mdui-color-text-secondary);
        ">
                您当前未进入任何班级
            </span>

            <!-- 输入框 -->
            <mdui-text-field ref="invitecodeField" v-model="inviteCode" variant="outlined" label="邀请码"
                style="margin-top: 12px; width: 100%;" />
            <div style="
          position: absolute;
          left: 8px;
          bottom: 18px;
          color: rgb(var(--mdui-color-primary-light));
          background-color: transparent;
        ">
                <mdui-button type="button"
                    style="color: rgb(var(--mdui-color-primary-light)); background-color: transparent;" @click=logout()>
                    退出登录</mdui-button>
            </div>

            <div style="position: absolute; right: 18px; bottom: 18px;">
                <mdui-button type="submit" @click="handleJoin">
                    加入
                </mdui-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { joinClass } from "../api/classes";
import { useGlobalStore } from '../stores/global'
import { logoutApi } from '../api/auth'
const globalStore = useGlobalStore()
const invitecodeField = ref(null)
import { useRouter } from 'vue-router';
const router = useRouter();
const inviteCode = ref("");
const handleJoin = async () => {
    if (!inviteCode.value) {
        invitecodeField.value?.setCustomValidity('邀请码不能为空')
        invitecodeField.value?.reportValidity()
        return;
    }
    invitecodeField.value?.setCustomValidity('')
    invitecodeField.value?.reportValidity()


    try {
        const res = await joinClass(inviteCode.value);
        const classUuid = res.data.data.class_uuid;
        globalStore.setClassUuids([...globalStore.classUuids, classUuid]);
        router.push({ name: 'Home' });
    } catch (err) {
        if (err.response?.data?.message) {
            invitecodeField.value?.setCustomValidity(err.response.data.message);
            invitecodeField.value?.reportValidity();
        }
    }
};
function logout() {
    logoutApi()
    localStorage.removeItem('access_token')
    router.push('/login')
}
onMounted(async () => {     
if (globalStore.classUuids.length && localStorage.getItem('access_token') !== null) {
    router.replace({ name: 'Home' })
    return
}
else if (!globalStore.classUuids.length && localStorage.getItem('access_token') !== null) {
    router.replace({ name: 'Invite' })
    return
}

})
</script>
