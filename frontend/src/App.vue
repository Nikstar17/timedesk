<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HeaderView from './views/HeaderView.vue'
</script>

<template>
  <header>
    <HeaderView />
  </header>
  <main>
    <RouterView />
  </main>
</template>

<style scoped></style>
