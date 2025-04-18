<template>
  <div class="projects-container">
    <h2 class="text-2xl font-bold mb-4">Meine Projekte</h2>

    <div v-if="loading" class="loading-indicator">
      <p>Projekte werden geladen...</p>
    </div>

    <div
      v-else-if="error"
      class="error-message bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
    >
      {{ error }}
    </div>

    <div v-else-if="projects.length === 0" class="no-projects bg-gray-100 p-4 rounded text-center">
      <p>Du hast noch keine Projekte angelegt.</p>
    </div>

    <div v-else class="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card bg-white p-4 rounded shadow-md hover:shadow-lg transition-shadow"
      >
        <h3 class="text-xl font-semibold mb-2">{{ project.name }}</h3>
        <p class="text-gray-600 mb-3">{{ project.description }}</p>
        <div class="flex justify-between items-center text-sm text-gray-500">
          <span>Erstellt: {{ formatDate(project.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchWithAuth } from '../utils/api'
import { API_BASE_URL } from '../utils/config'

interface Project {
  id: string
  name: string
  description: string
  created_at: string
}

const projects = ref<Project[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

async function fetchProjects() {
  loading.value = true
  error.value = null

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/project`)

    if (response.ok) {
      const data = await response.json()
      projects.value = data.projects || []
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Laden der Projekte'
    }
  } catch (e) {
    console.error('Fehler beim Abrufen der Projekte:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.projects-container {
  width: 100%;
  padding: 1rem;
}

.loading-indicator,
.no-projects {
  padding: 2rem;
  text-align: center;
}

.project-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
