<template>
  <header>
    <HeaderView />
  </header>
  <main class="container mx-auto px-4 py-6">
    <ShowProjects />
    <div class="mt-8">
      <CreateProject />
    </div>
  </main>
</template>

<script setup lang="ts">
import CreateProject from '@/components/CreateProject.vue'
import ShowProjects from '@/components/ShowProjects.vue'
import HeaderView from './HeaderView.vue'
</script>
