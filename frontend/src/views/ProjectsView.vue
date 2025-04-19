<template>
  <header>
    <HeaderView />
  </header>
  <main>
    <div>
      <p class="text-yellow-600 bg-yellow-100 p-3 rounded border border-yellow-300">
        <strong>Hinweis:</strong> Zurzeit kann es vereinzelt zu Anzeigefehlern kommen. Alle Zeiten
        werden jedoch korrekt in der Datenbank gespeichert.
      </p>
    </div>
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
