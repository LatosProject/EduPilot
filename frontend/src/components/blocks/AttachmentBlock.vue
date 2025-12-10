<template>
  <a :href="data.url" target="_blank">📎 {{ data.name }}</a>
</template>

<script setup>
defineProps({ data: Object })
</script>
