<template>
<mdui-button variant="text" :href="data.url" target="_blank" rel="noopener noreferrer" icon="attach_email">
  {{ data.name }}
</mdui-button>
</template>

<script setup>
defineProps({ data: Object })
</script>
