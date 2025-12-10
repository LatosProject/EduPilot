<template>
  <div
    class="mdui-prose"
    style="
      height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
    "
  >
    <h1 style="font-size: 96px; margin: 0;">404</h1>
    <p style="font-size: 20px; margin-top: 16px;">页面不存在</p>
      <mdui-button variant="filled" color="primary" @click="$router.replace({ name: 'Home' })">
        返回首页
      </mdui-button>
  </div>
</template>

<script>
export default {
  name: "NotFound"
}
</script>
