<template>
  <header>
    <HeaderView />
  </header>
  <main>
    <div class="mt-8">
      <CreateProject @project-created="refreshProjects" />
    </div>
    <ShowProjects ref="projectsListRef" />
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CreateProject from '@/components/CreateProject.vue'
import ShowProjects from '@/components/ShowProjects.vue'
import HeaderView from './HeaderView.vue'

const projectsListRef = ref<InstanceType<typeof ShowProjects> | null>(null)

function refreshProjects() {
  projectsListRef.value?.fetchProjects()
}
</script>
