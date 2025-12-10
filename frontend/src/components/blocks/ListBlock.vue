<template>
  <ul>
    <li v-for="(i, index) in data.items" :key="index">{{ i }}</li>
  </ul>
</template>

<script setup>
defineProps({ data: Object })
</script>
