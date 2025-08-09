<template>
  <mdui-card style="
      cursor: default;
      border-radius: var(--mdui-shape-corner-extra-large);
      height: 56px;
      display: flex;
      align-items: center;
      padding: 0;
      gap: 0;
      box-shadow: none;
      background-color: rgb(var(--mdui-color-surface-container-high));
    ">
    <mdui-icon name="search" style="
        font-size: 24px;
        color: rgb(var(--mdui-color-on-surface-variant));
        margin: 0 16px;
        user-select: none;
      "></mdui-icon>

    <div style="
        font-size: 16px;
        line-height: 24px;
        letter-spacing: 0.5px;
        font-weight: 400;
        font-family: 'Roboto';
        user-select: none;
        color: rgb(var(--mdui-color-on-surface-variant));
      ">
      搜索
    </div>
    <template v-if="user && user.avatar_url">
      <mdui-button-icon style="margin-left: auto; margin-right: 8px">
        <img :src="user.avatar_url" style="background-color:#ffff" alt="avatar" />
      </mdui-button-icon>
    </template>
    <template v-else>
      <mdui-button-icon icon="account_circle" style="margin-left: auto; margin-right: 8px"></mdui-button-icon>
    </template>
  </mdui-card>
</template>
<script setup>
import { ref } from 'vue';
import { onMounted } from 'vue';
import { getProfile } from '../../api/auth';
const user = ref(null)
onMounted(async () => {
  try {
    const res = await getProfile()
    user.value = res.data.data
  } catch (error) {
    user.value = null
  }
})

</script>
