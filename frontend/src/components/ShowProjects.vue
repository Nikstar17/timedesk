<template>
  <div class="projects-container">
    <h2 class="text-2xl font-bold mb-4">Meine Projekte</h2>

    <!-- Time Tracking Control Panel -->
    <div
      class="time-tracking-panel bg-blue-50 p-4 mb-6 rounded-lg shadow-sm border border-blue-200"
    >
      <div v-if="timeTrackingStatus === 'idle'">
        <p class="text-blue-800 font-medium">Keine aktive Zeiterfassung</p>
        <p class="text-sm text-blue-600 mt-1">
          Klicke auf "Erfassung starten" bei einem Projekt, um Zeit zu erfassen.
        </p>
      </div>

      <div v-else class="flex flex-col">
        <div class="flex justify-between items-center">
          <p class="text-blue-800 font-medium">
            <span v-if="timeTrackingStatus === 'tracking'">📊 Aktive Zeiterfassung für:</span>
            <span v-else-if="timeTrackingStatus === 'paused'">⏸️ Pausierte Zeiterfassung für:</span>
            <span class="font-bold ml-2">{{ getActiveProjectName() }}</span>
          </p>

          <!-- Live timer display -->
          <div class="flex items-center">
            <div v-if="timeTrackingStatus === 'tracking'" class="text-blue-800 font-bold text-xl">
              {{ currentTimerFormatted }}
            </div>
            <div
              v-else-if="timeTrackingStatus === 'paused'"
              class="text-gray-600 font-bold text-xl"
            >
              {{ currentTimerFormatted }} (pausiert)
            </div>
          </div>
        </div>

        <div class="flex mt-2 space-x-2">
          <button
            v-if="timeTrackingStatus === 'tracking'"
            @click="pauseTimeTracking"
            class="bg-yellow-500 hover:bg-yellow-600 text-white py-1 px-3 rounded text-sm"
          >
            Pausieren
          </button>

          <button
            v-if="timeTrackingStatus === 'paused'"
            @click="resumeTimeTracking"
            class="bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded text-sm"
          >
            Fortsetzen
          </button>

          <button
            v-if="timeTrackingStatus === 'tracking' || timeTrackingStatus === 'paused'"
            @click="stopTimeTracking"
            class="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded text-sm"
          >
            Beenden
          </button>
        </div>
      </div>
    </div>

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

    <!-- Projektkarten-Ansicht -->
    <div
      v-else-if="!showTimeEntriesForProject"
      class="projects-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card bg-white p-4 rounded shadow-md hover:shadow-lg transition-shadow"
      >
        <h3 class="text-xl font-semibold mb-2">{{ project.name }}</h3>
        <p class="text-gray-600 mb-3">{{ project.description }}</p>

        <!-- Time Statistics Section -->
        <div class="time-statistics border-t border-gray-200 pt-3 mt-3">
          <h4 class="font-medium text-sm text-gray-700 mb-2">Zeitstatistik</h4>

          <!-- Total Project Time -->
          <div class="time-stat-row flex justify-between text-sm">
            <span class="text-gray-600">Gesamtzeit:</span>
            <span class="font-medium">
              {{
                projectTimeStatistics[project.id]
                  ? formatTimeDisplay(projectTimeStatistics[project.id].total_time)
                  : '00:00:00'
              }}
            </span>
          </div>

          <!-- Total Pause Time -->
          <div class="time-stat-row flex justify-between text-sm">
            <span class="text-gray-600">Pausenzeit:</span>
            <span class="font-medium">
              {{
                projectTimeStatistics[project.id]
                  ? formatTimeDisplay(projectTimeStatistics[project.id].total_pause_time)
                  : '00:00:00'
              }}
            </span>
          </div>

          <!-- Active Session Info (if project is currently being tracked) -->
          <div
            v-if="projectTimeStatistics[project.id]?.is_active"
            class="mt-2 bg-blue-50 p-2 rounded"
          >
            <div class="text-sm text-blue-700 font-medium">
              {{ projectTimeStatistics[project.id]?.is_paused ? '⏸️ Pausiert' : '▶️ Aktiv' }}
              {{ formatTimeSince(projectTimeStatistics[project.id]?.active_since) }}
            </div>
            <div class="flex justify-between text-sm mt-1">
              <span class="text-blue-600">Aktuelle Sitzung:</span>
              <span
                class="font-medium"
                :class="{
                  'text-blue-800': !projectTimeStatistics[project.id]?.is_paused,
                  'text-gray-600': projectTimeStatistics[project.id]?.is_paused,
                }"
              >
                {{
                  activeTimeEntry?.project_id === project.id
                    ? currentTimerFormatted
                    : formatTimeDisplay(projectTimeStatistics[project.id]?.current_session_time)
                }}
                {{ projectTimeStatistics[project.id]?.is_paused ? '(pausiert)' : '' }}
              </span>
            </div>
          </div>
        </div>

        <div class="mt-3 flex flex-col space-y-2">
          <!-- Zeiteinträge-Button -->
          <button
            @click="showTimeEntriesForProject = project"
            class="w-full bg-indigo-100 hover:bg-indigo-200 text-indigo-700 py-2 px-4 rounded flex items-center justify-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            Zeiteinträge anzeigen
          </button>

          <!-- Time tracking button -->
          <button
            v-if="timeTrackingStatus === 'idle'"
            @click="startTimeTracking(project.id)"
            class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded flex items-center justify-center"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Zeit erfassen
          </button>

          <button
            v-else-if="activeTimeEntry?.project_id === project.id"
            disabled
            class="w-full bg-gray-300 text-gray-600 py-2 px-4 rounded flex items-center justify-center cursor-not-allowed"
          >
            {{ timeTrackingStatus === 'tracking' ? '⏺️ Wird erfasst' : '⏸️ Pausiert' }}
          </button>

          <button
            v-else
            disabled
            class="w-full bg-gray-200 text-gray-500 py-2 px-4 rounded flex items-center justify-center cursor-not-allowed"
          >
            Andere Erfassung aktiv
          </button>
        </div>

        <div class="flex justify-between items-center text-sm text-gray-500 mt-3">
          <span>Erstellt: {{ formatDate(project.created_at) }}</span>
          <button
            @click="confirmDeleteProject(project)"
            class="text-red-600 hover:text-red-800 transition-colors"
            title="Projekt löschen"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Zeiteinträge-Ansicht -->
    <div v-else-if="showTimeEntriesForProject" class="time-entries-view">
      <ProjectTimeEntries
        :project-id="showTimeEntriesForProject.id"
        :project-name="showTimeEntriesForProject.name"
        @close="showTimeEntriesForProject = null"
      />
    </div>

    <!-- Lösch-Bestätigungsdialog -->
    <div
      v-if="showDeleteDialog"
      class="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Projekt löschen</h3>
        <p class="mb-6">
          Möchtest du das Projekt "{{ projectToDelete?.name }}" wirklich löschen? Diese Aktion kann
          nicht rückgängig gemacht werden.
        </p>
        <div class="flex justify-end space-x-3">
          <button
            @click="cancelDelete"
            class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
          >
            Abbrechen
          </button>
          <button
            @click="deleteProject"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineExpose, onUnmounted, computed, inject, provide, watch } from 'vue'
import { fetchWithAuth } from '../utils/api'
import { API_BASE_URL } from '../utils/config'
import ProjectTimeEntries from './ProjectTimeEntries.vue'

// Inject the global time tracking state
const globalIsTimeTrackingActive = inject('isTimeTrackingActive', ref(false))

interface Project {
  id: string
  name: string
  description: string
  created_at: string
}

// Type for active time tracking entries
interface TimeEntry {
  id: string
  project_id: string
  start_time: string
  end_time: string | null
}

// Interface for time statistics
interface TimeDisplay {
  hours: number
  minutes: number
  seconds: number
}

interface ProjectTimeStatistics {
  total_time: TimeDisplay
  total_pause_time: TimeDisplay
  is_active: boolean
  is_paused: boolean
  active_since?: string
  current_session_time?: TimeDisplay
}

const projects = ref<Project[]>([])
const activeTimeEntry = ref<TimeEntry | null>(null)
const activePauseId = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const showDeleteDialog = ref(false)
const projectToDelete = ref<Project | null>(null)
const deleteLoading = ref(false)
const timeTrackingStatus = ref<'idle' | 'tracking' | 'paused'>('idle')
const projectTimeStatistics = ref<Record<string, ProjectTimeStatistics>>({})
const currentTimer = ref<{ hours: number; minutes: number; seconds: number }>({
  hours: 0,
  minutes: 0,
  seconds: 0,
})
let timerInterval: number | null = null

// New state for time entries view
const showTimeEntriesForProject = ref<Project | null>(null)

// Provide timer information for child components (like ProjectTimeEntries)
provide('currentTimer', currentTimer)
provide(
  'isTracking',
  computed(() => timeTrackingStatus.value === 'tracking'),
)
provide(
  'activeProjectId',
  computed(() => activeTimeEntry.value?.project_id || ''),
)

// Provide a more comprehensive global tracking state for child components
const globalTrackingState = ref({
  isTracking: timeTrackingStatus.value === 'tracking',
  isPaused: timeTrackingStatus.value === 'paused',
  activeEntryId: activeTimeEntry.value?.id || null,
})

// Provide this state to child components
provide('globalTrackingState', globalTrackingState)

// Update the global tracking state whenever local state changes
watch(
  [timeTrackingStatus, activeTimeEntry],
  ([newStatus, newEntry]) => {
    globalTrackingState.value = {
      isTracking: newStatus === 'tracking',
      isPaused: newStatus === 'paused',
      activeEntryId: newEntry?.id || null,
    }
  },
  { immediate: true },
)

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

function confirmDeleteProject(project: Project) {
  projectToDelete.value = project
  showDeleteDialog.value = true
}

function cancelDelete() {
  showDeleteDialog.value = false
  projectToDelete.value = null
}

async function deleteProject() {
  if (!projectToDelete.value) return

  deleteLoading.value = true

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/project/${projectToDelete.value.id}`, {
      method: 'DELETE',
    })

    if (response.ok) {
      // Projekt aus der lokalen Liste entfernen
      projects.value = projects.value.filter((p) => p.id !== projectToDelete.value?.id)
      showDeleteDialog.value = false
      projectToDelete.value = null
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Löschen des Projekts'
    }
  } catch (e) {
    console.error('Fehler beim Löschen des Projekts:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  } finally {
    deleteLoading.value = false
  }
}

// Format time display as HH:MM:SS
function formatTimeDisplay(time: TimeDisplay | undefined): string {
  if (!time) return '00:00:00'
  return [
    time.hours.toString().padStart(2, '0'),
    time.minutes.toString().padStart(2, '0'),
    time.seconds.toString().padStart(2, '0'),
  ].join(':')
}

// Format time since when a timer was started
function formatTimeSince(dateString: string | undefined): string {
  if (!dateString) return ''
  const startDate = new Date(dateString)
  const now = new Date()
  const diffInMs = now.getTime() - startDate.getTime()

  const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60))
  const diffInMinutes = Math.floor((diffInMs % (1000 * 60 * 60)) / (1000 * 60))

  if (diffInHours > 0) {
    return `seit ${diffInHours}h ${diffInMinutes}m`
  } else {
    return `seit ${diffInMinutes}m`
  }
}

async function fetchProjectTimeStatistics() {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/project-time-statistics`)

    if (response.ok) {
      const data = await response.json()
      projectTimeStatistics.value = data.statistics || {}
    } else {
      console.error('Failed to fetch project time statistics')
    }
  } catch (e) {
    console.error('Error fetching project time statistics:', e)
  }
}

async function fetchProjects() {
  loading.value = true
  error.value = null

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/project`)

    if (response.ok) {
      const data = await response.json()
      projects.value = data.projects || []
      // Fetch time statistics after projects are loaded
      await fetchProjectTimeStatistics()
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

async function checkActiveTimeEntry() {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/active-time-entry`)

    if (response.ok) {
      const data = await response.json()

      if (data.active_entry) {
        // Set active time entry
        activeTimeEntry.value = {
          id: data.active_entry.id,
          project_id: data.active_entry.project_id,
          start_time: data.active_entry.start_time,
          end_time: null,
        }

        // Set tracking status based on pause status
        if (data.active_entry.is_paused) {
          timeTrackingStatus.value = 'paused'
          activePauseId.value = data.active_entry.pause_id
        } else {
          timeTrackingStatus.value = 'tracking'
        }

        // Update the global time tracking state
        globalIsTimeTrackingActive.value = true
      } else {
        // No active time entry
        timeTrackingStatus.value = 'idle'
        activeTimeEntry.value = null
        activePauseId.value = null

        // Update the global time tracking state
        globalIsTimeTrackingActive.value = false
      }
    } else {
      console.error('Failed to check active time entry')
    }
  } catch (e) {
    console.error('Error checking active time entry:', e)
  }
}

async function startTimeTracking(projectId: string) {
  if (timeTrackingStatus.value !== 'idle') {
    error.value = 'Es läuft bereits eine Zeiterfassung. Bitte stoppe diese zuerst.'
    return
  }

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/start-time-entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        project_id: projectId,
      }),
    })

    if (response.ok) {
      // Fetch the active time entry to get the created ID
      await checkActiveTimeEntry()
      // Immediately fetch time statistics to get current session info
      await fetchProjectTimeStatistics()
      // Start the timer
      startTimerUpdates()
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Starten der Zeiterfassung'
    }
  } catch (e) {
    console.error('Fehler beim Starten der Zeiterfassung:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  }
}

async function pauseTimeTracking() {
  if (timeTrackingStatus.value !== 'tracking' || !activeTimeEntry.value) {
    error.value = 'Es läuft keine Zeiterfassung, die pausiert werden kann.'
    return
  }

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/start-time-pause`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        time_entries_id: activeTimeEntry.value.id,
      }),
    })

    if (response.ok) {
      // Fetch the active time entry to get the pause ID
      await checkActiveTimeEntry()
      // Stop the timer
      if (timerInterval) {
        clearInterval(timerInterval)
        timerInterval = null
      }
      // Update statistics to reflect pause
      await fetchProjectTimeStatistics()
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Pausieren der Zeiterfassung'
    }
  } catch (e) {
    console.error('Fehler beim Pausieren der Zeiterfassung:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  }
}

async function resumeTimeTracking() {
  if (timeTrackingStatus.value !== 'paused' || !activePauseId.value) {
    error.value = 'Es gibt keine pausierte Zeiterfassung, die fortgesetzt werden kann.'
    return
  }

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/end-time-pause`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        time_pause_id: activePauseId.value,
      }),
    })

    if (response.ok) {
      // Update the tracking status
      await checkActiveTimeEntry()
      // Update statistics
      await fetchProjectTimeStatistics()
      // Restart the timer
      startTimerUpdates()
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Fortsetzen der Zeiterfassung'
    }
  } catch (e) {
    console.error('Fehler beim Fortsetzen der Zeiterfassung:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  }
}

async function stopTimeTracking() {
  if (timeTrackingStatus.value === 'idle' || !activeTimeEntry.value) {
    error.value = 'Es läuft keine Zeiterfassung, die gestoppt werden kann.'
    return
  }

  // If we're paused, end the pause first
  if (timeTrackingStatus.value === 'paused' && activePauseId.value) {
    await resumeTimeTracking()
  }

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/stop-time-entry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        time_entry_id: activeTimeEntry.value.id,
      }),
    })

    if (response.ok) {
      timeTrackingStatus.value = 'idle'
      activeTimeEntry.value = null
      activePauseId.value = null

      // Stop the timer
      if (timerInterval) {
        clearInterval(timerInterval)
        timerInterval = null
      }

      // Update statistics immediately to reflect the ended session
      await fetchProjectTimeStatistics()
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Beenden der Zeiterfassung'
    }
  } catch (e) {
    console.error('Fehler beim Beenden der Zeiterfassung:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  }
}

// Function to get the currently active project name
function getActiveProjectName(): string | null {
  if (!activeTimeEntry.value) return null

  const activeProject = projects.value.find((p) => p.id === activeTimeEntry.value?.project_id)
  return activeProject?.name || null
}

// Function to update the current timer
function updateCurrentTimer() {
  if (!activeTimeEntry.value || timeTrackingStatus.value === 'idle') return

  const projectId = activeTimeEntry.value.project_id
  const stats = projectTimeStatistics.value[projectId]

  if (!stats || !stats.is_active) return

  if (stats.current_session_time) {
    // Deep copy the current session time
    currentTimer.value = {
      hours: stats.current_session_time.hours,
      minutes: stats.current_session_time.minutes,
      seconds: stats.current_session_time.seconds,
    }
  } else {
    currentTimer.value = { hours: 0, minutes: 0, seconds: 0 }
  }
}

// Function to increment timer every second
function startTimerUpdates() {
  // Clear any existing interval
  if (timerInterval) {
    clearInterval(timerInterval)
  }

  // Only start timer if we're actively tracking (not paused)
  if (timeTrackingStatus.value === 'tracking') {
    // Initialize the timer with current values
    updateCurrentTimer()

    timerInterval = window.setInterval(() => {
      if (timeTrackingStatus.value !== 'tracking') return

      // Increment seconds
      currentTimer.value.seconds++

      // Handle minute rollover
      if (currentTimer.value.seconds >= 60) {
        currentTimer.value.seconds = 0
        currentTimer.value.minutes++

        // Handle hour rollover
        if (currentTimer.value.minutes >= 60) {
          currentTimer.value.minutes = 0
          currentTimer.value.hours++
        }
      }

      // Synchronisiere das aktive Projekt mit dem Timer
      updateActiveProjectStatistics()
    }, 1000)
  }
}

// Neue Funktion: Aktualisiere die Projektstatistik für das aktive Projekt mit dem lokalen Timer
function updateActiveProjectStatistics() {
  if (!activeTimeEntry.value || timeTrackingStatus.value !== 'tracking') return

  const projectId = activeTimeEntry.value.project_id

  // Überprüfe, ob das Projekt in den Statistiken existiert
  if (projectTimeStatistics.value[projectId]) {
    // Aktualisiere die aktuelle Sitzungszeit mit dem lokalen Timer
    if (!projectTimeStatistics.value[projectId].current_session_time) {
      projectTimeStatistics.value[projectId].current_session_time = {
        hours: 0,
        minutes: 0,
        seconds: 0,
      }
    }

    // Synchronisiere die Zeiten
    projectTimeStatistics.value[projectId].current_session_time.hours = currentTimer.value.hours
    projectTimeStatistics.value[projectId].current_session_time.minutes = currentTimer.value.minutes
    projectTimeStatistics.value[projectId].current_session_time.seconds = currentTimer.value.seconds
  }
}

// Format the current timer as HH:MM:SS
const currentTimerFormatted = computed(() => {
  return [
    currentTimer.value.hours.toString().padStart(2, '0'),
    currentTimer.value.minutes.toString().padStart(2, '0'),
    currentTimer.value.seconds.toString().padStart(2, '0'),
  ].join(':')
})

// Add beforeunload event handler to prevent accidental page closing during time tracking
// This has been moved to the App.vue component for global handling
function setupBeforeUnloadHandler() {
  // Empty function as we're now handling this at the App level
  // The App component will show a custom dialog instead of the browser's native one
}

// Refresh statistics periodically if there's an active tracking
function setupStatisticsRefresh() {
  if (timeTrackingStatus.value !== 'idle') {
    // Start the timer updates if we're tracking
    if (timeTrackingStatus.value === 'tracking') {
      startTimerUpdates()
    }

    // No interval-based fetching needed for normal operation
    // The data is only updated on the server when the user takes an action (start, pause, resume, stop)
    // So we'll fetch data only on those specific events
  }
}

onMounted(async () => {
  await fetchProjects()
  await checkActiveTimeEntry()
  if (timeTrackingStatus.value !== 'idle') {
    await fetchProjectTimeStatistics()
    updateCurrentTimer()
  }
  setupStatisticsRefresh()
  setupBeforeUnloadHandler()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
})

defineExpose({
  fetchProjects,
  checkActiveTimeEntry,
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
