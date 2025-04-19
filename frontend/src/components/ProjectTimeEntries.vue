<template>
  <div class="time-entries-container">
    <h3 class="text-xl font-semibold mb-4">Zeiteinträge für "{{ projectName }}"</h3>

    <div v-if="loading" class="loading-state">
      <p>Lade Zeiteinträge...</p>
    </div>

    <div
      v-else-if="error"
      class="error-state bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
    >
      {{ error }}
    </div>

    <div v-else-if="!timeEntries.length" class="empty-state text-center py-8 bg-gray-50 rounded">
      <p>Keine Zeiteinträge für dieses Projekt gefunden.</p>
    </div>

    <div v-else class="entries-table">
      <table class="min-w-full bg-white border border-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Datum</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Start</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Ende</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Gesamtzeit</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Pausenzeit</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Effektive Zeit</th>
            <th class="px-4 py-2 text-left text-sm font-medium text-gray-600">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in timeEntries"
            :key="entry.id"
            :class="{ 'bg-blue-50': entry.is_active }"
            class="border-b border-gray-200 hover:bg-gray-50"
            @click="toggleEntryDetails(entry)"
          >
            <td class="px-4 py-3 text-sm">{{ formatDate(entry.start_time) }}</td>
            <td class="px-4 py-3 text-sm">{{ formatTime(entry.start_time) }}</td>
            <td class="px-4 py-3 text-sm">
              {{ entry.end_time ? formatTime(entry.end_time) : '-' }}
            </td>
            <td class="px-4 py-3 text-sm">{{ formatDuration(entry.total_duration) }}</td>
            <td class="px-4 py-3 text-sm">
              <span v-if="isEntryPaused(entry) && entry.is_active">
                {{ getLivePauseDuration(entry) }}
              </span>
              <span v-else>
                {{ formatDuration(entry.pause_duration) }}
              </span>
            </td>
            <td class="px-4 py-3 text-sm font-medium">
              {{ formatDuration(entry.effective_duration) }}
            </td>
            <td class="px-4 py-3 text-sm">
              <span
                v-if="entry.is_active"
                class="inline-block px-2 py-1 text-xs font-medium rounded-full"
                :class="
                  isEntryPaused(entry)
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
                "
              >
                {{ isEntryPaused(entry) ? 'Pausiert' : 'Aktiv' }}
              </span>
              <span
                v-else
                class="inline-block px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800"
              >
                Abgeschlossen
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pause details expansion -->
      <div v-if="expandedEntry" class="mt-4 p-4 bg-gray-50 rounded">
        <h4 class="font-medium mb-2">
          Pausendetails für Eintrag vom {{ formatDate(expandedEntry.start_time) }}
        </h4>
        <div v-if="!expandedEntry.pauses.length" class="text-sm text-gray-600">
          Keine Pausen in diesem Zeiteintrag
        </div>
        <table v-else class="min-w-full bg-white border border-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-600">Pause Start</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-600">Pause Ende</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-600">Dauer</th>
              <th class="px-4 py-2 text-left text-xs font-medium text-gray-600">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="pause in expandedEntry.pauses"
              :key="pause.id"
              class="border-b border-gray-200"
            >
              <td class="px-4 py-2 text-xs">{{ formatDateTime(pause.start_time) }}</td>
              <td class="px-4 py-2 text-xs">
                {{ pause.end_time ? formatDateTime(pause.end_time) : '-' }}
              </td>
              <td class="px-4 py-2 text-xs">
                <span v-if="pause.is_active">
                  {{ getLiveActivePauseDuration(pause) }}
                </span>
                <span v-else>
                  {{ pause.end_time ? calculatePauseDuration(pause) : 'Läuft...' }}
                </span>
              </td>
              <td class="px-4 py-2 text-xs">
                <span
                  v-if="pause.is_active"
                  class="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800"
                >
                  Aktiv
                </span>
                <span
                  v-else
                  class="inline-block px-2 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-800"
                >
                  Beendet
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="mt-4">
      <button
        @click="$emit('close')"
        class="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded transition-colors"
      >
        Zurück
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  ref,
  onMounted,
  onUnmounted,
  defineProps,
  defineEmits,
  watch,
  inject,
  computed,
  nextTick,
} from 'vue'
import { fetchWithAuth } from '../utils/api'
import { API_BASE_URL } from '../utils/config'
import { DateTime } from 'luxon'

const props = defineProps<{
  projectId: string
  projectName: string
}>()

defineEmits(['close'])

// Injiziere den globalen Timer aus der ShowProjects-Komponente, falls vorhanden
const globalCurrentTimer = inject('currentTimer', ref({ hours: 0, minutes: 0, seconds: 0 }))
const globalIsTracking = inject('isTracking', ref(false))
const globalActiveProjectId = inject('activeProjectId', ref(''))

// Kommunikationszustand mit der Eltern-Komponente
const globalTracking = inject(
  'globalTrackingState',
  ref({ isTracking: false, isPaused: false, activeEntryId: null }),
)

// Reaktiver Berechnungswert: Ist der aktuelle Zeiteintrag der global aktive Eintrag?
const isGlobalActiveEntry = computed(() => {
  const activeEntry = timeEntries.value.find((entry) => entry.is_active)
  return activeEntry && globalTracking.value.activeEntryId === activeEntry.id
})

interface TimeDisplay {
  hours: number
  minutes: number
  seconds: number
}

interface PauseInfo {
  id: string
  start_time: string
  end_time: string | null
  is_active: boolean
}

interface TimeEntry {
  id: string
  start_time: string
  end_time: string | null
  is_active: boolean
  total_duration: TimeDisplay
  pause_duration: TimeDisplay
  effective_duration: TimeDisplay
  pauses: PauseInfo[]
}

const timeEntries = ref<TimeEntry[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const expandedEntry = ref<TimeEntry | null>(null)
let refreshInterval: number | null = null
let pauseTimerInterval: number | null = null
const currentPauseTimer = ref<Record<string, TimeDisplay>>({})
const realTotalDurations = ref<Record<string, TimeDisplay>>({})

// Format functions
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

function formatTime(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function formatDuration(duration?: TimeDisplay): string {
  if (!duration) return '00:00:00'
  return [
    duration.hours.toString().padStart(2, '0'),
    duration.minutes.toString().padStart(2, '0'),
    duration.seconds.toString().padStart(2, '0'),
  ].join(':')
}

// Calculate pause duration
function calculatePauseDuration(pause: PauseInfo): string {
  if (!pause.end_time) return '--:--:--'

  const start = new Date(pause.start_time)
  const end = new Date(pause.end_time)
  const diffMs = end.getTime() - start.getTime()

  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diffMs % (1000 * 60)) / 1000)

  return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

// Get live pause duration for an active pause
function getLiveActivePauseDuration(pause: PauseInfo): string {
  if (!pause.is_active) return calculatePauseDuration(pause)

  if (currentPauseTimer.value[pause.id]) {
    return formatDuration(currentPauseTimer.value[pause.id])
  }

  return '00:00:00'
}

// Get the combined live pause duration for an entry with active pauses
function getLivePauseDuration(entry: TimeEntry): string {
  if (!isEntryPaused(entry) || !entry.is_active) return formatDuration(entry.pause_duration)

  // Get the base pause duration from already completed pauses
  const basePauseDuration = { ...entry.pause_duration }

  // Find the active pause
  const activePause = entry.pauses.find((p) => p.is_active)
  if (!activePause) return formatDuration(basePauseDuration)

  // If we have a current timer for this pause, add it to the base duration
  if (currentPauseTimer.value[activePause.id]) {
    const currentTimer = currentPauseTimer.value[activePause.id]

    // Calculate total seconds
    let totalSeconds =
      basePauseDuration.hours * 3600 +
      basePauseDuration.minutes * 60 +
      basePauseDuration.seconds +
      currentTimer.hours * 3600 +
      currentTimer.minutes * 60 +
      currentTimer.seconds

    // Convert back to hours, minutes, seconds
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60

    return formatDuration({ hours, minutes, seconds })
  }

  return formatDuration(basePauseDuration)
}

// Check if an entry is currently paused
function isEntryPaused(entry: TimeEntry): boolean {
  if (!entry.is_active) return false
  return entry.pauses.some((pause) => pause.is_active)
}

// Toggle expanded entry details
function toggleEntryDetails(entry: TimeEntry) {
  if (expandedEntry.value && expandedEntry.value.id === entry.id) {
    expandedEntry.value = null
  } else {
    expandedEntry.value = entry
  }
}

// Function to update active pause timers
function updatePauseTimers() {
  // For each time entry
  timeEntries.value.forEach((entry) => {
    // If entry is active
    if (entry.is_active) {
      const isCurrentActiveTrackedEntry =
        entry.id === globalTracking.value.activeEntryId &&
        !isEntryPaused(entry) &&
        globalIsTracking.value

      // Nur die Gesamtzeit für Einträge aktualisieren, die nicht aktiv getrackt werden oder pausiert sind
      // Aktiv getrackte Einträge ohne Pause werden durch updateActiveTimeEntry() gesteuert
      if (!isCurrentActiveTrackedEntry) {
        updateEntryTotalDuration(entry)
      }

      // Wenn pausiert, auch den Pausentimer aktualisieren
      if (isEntryPaused(entry)) {
        // Find the active pause
        const activePause = entry.pauses.find((p) => p.is_active)
        if (activePause) {
          // Initialize timer if not already set
          if (!currentPauseTimer.value[activePause.id]) {
            // Calculate current duration from pause start until now
            const start = new Date(activePause.start_time)
            const now = new Date()
            const diffMs = now.getTime() - start.getTime()

            currentPauseTimer.value[activePause.id] = {
              hours: Math.floor(diffMs / (1000 * 60 * 60)),
              minutes: Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60)),
              seconds: Math.floor((diffMs % (1000 * 60)) / 1000),
            }
          } else {
            // Increment existing timer by 1 second
            let seconds = currentPauseTimer.value[activePause.id].seconds + 1
            let minutes = currentPauseTimer.value[activePause.id].minutes
            let hours = currentPauseTimer.value[activePause.id].hours

            if (seconds >= 60) {
              seconds = 0
              minutes++
              if (minutes >= 60) {
                minutes = 0
                hours++
              }
            }

            currentPauseTimer.value[activePause.id] = { hours, minutes, seconds }
          }

          // Aktualisiere die effektive Zeit, indem die aktuelle Pausenzeit abgezogen wird
          updateEntryEffectiveDuration(entry)
        }
      }
    }
  })
}

// Neue Funktion: Aktualisiere die Gesamtzeit eines Eintrags basierend auf Start bis jetzt
function updateEntryTotalDuration(entry: TimeEntry) {
  if (!entry.is_active) return

  const start = new Date(entry.start_time)
  const now = new Date()
  const diffMs = now.getTime() - start.getTime()

  // Konvertiere die Millisekunden in Stunden, Minuten, Sekunden
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diffMs % (1000 * 60)) / 1000)

  // Aktualisiere die Gesamtzeit des Eintrags
  entry.total_duration = { hours, minutes, seconds }
}

// Neue Funktion: Aktualisiere die effektive Zeit (Gesamtzeit minus Pausenzeit)
function updateEntryEffectiveDuration(entry: TimeEntry) {
  if (!entry.is_active) return

  // Gesamtsekunden der Eintragsdauer berechnen
  const totalSeconds =
    entry.total_duration.hours * 3600 +
    entry.total_duration.minutes * 60 +
    entry.total_duration.seconds

  // Basis-Pausenzeit aus den abgeschlossenen Pausen
  let basePauseSeconds =
    entry.pause_duration.hours * 3600 +
    entry.pause_duration.minutes * 60 +
    entry.pause_duration.seconds

  // Aktive Pause finden und Zeit hinzufügen
  const activePause = entry.pauses.find((p) => p.is_active)
  if (activePause && currentPauseTimer.value[activePause.id]) {
    const pauseTimer = currentPauseTimer.value[activePause.id]
    basePauseSeconds += pauseTimer.hours * 3600 + pauseTimer.minutes * 60 + pauseTimer.seconds
  }

  // Effektive Zeit = Gesamtzeit - Pausenzeit
  const effectiveSeconds = Math.max(0, totalSeconds - basePauseSeconds)

  // Zurück in Stunden, Minuten, Sekunden umrechnen
  const hours = Math.floor(effectiveSeconds / 3600)
  const minutes = Math.floor((effectiveSeconds % 3600) / 60)
  const seconds = effectiveSeconds % 60

  // Aktualisiere die effektive Zeit des Eintrags
  entry.effective_duration = { hours, minutes, seconds }
}

// Funktion zur Initialisierung der Timer für alle aktiven Einträge
function initializeTimersForActiveEntries() {
  timeEntries.value.forEach((entry) => {
    if (entry.is_active) {
      // Initialisiere die Gesamtzeit des Eintrags
      updateEntryTotalDuration(entry)

      // Wenn der Eintrag pausiert ist, initialisiere auch die Pausenzeit
      if (isEntryPaused(entry)) {
        const activePause = entry.pauses.find((p) => p.is_active)
        if (activePause) {
          // Berechne die aktuelle Dauer der Pause
          const start = DateTime.fromISO(activePause.start_time, { zone: 'utc' }).setZone(
            'Europe/Berlin',
          )
          const now = DateTime.now().setZone('Europe/Berlin')
          const diff = now.diff(start, ['hours', 'minutes', 'seconds']).toObject()

          currentPauseTimer.value[activePause.id] = {
            hours: Math.floor(diff.hours ?? 0),
            minutes: Math.floor(diff.minutes ?? 0),
            seconds: Math.floor(diff.seconds ?? 0),
          }

          // Aktualisiere die effektive Zeit
          updateEntryEffectiveDuration(entry)
        }
      }
    }
  })
}

// Funktion zur Echtzeit-Aktualisierung des aktiven Zeiteintrags mit dem globalen Timer
function updateActiveTimeEntry() {
  // Wenn dieses Projekt nicht das aktiv getrackte Projekt ist, nichts tun
  if (!globalIsTracking.value || props.projectId !== globalActiveProjectId.value) return

  // Suche den aktiven Zeiteintrag, der nicht pausiert ist
  const activeEntry = timeEntries.value.find(
    (entry) =>
      entry.is_active && !isEntryPaused(entry) && entry.id === globalTracking.value.activeEntryId,
  )

  if (!activeEntry) return

  // Wenn wir von einer Pause kommen und der Eintrag gerade aktiviert wurde,
  // behalten wir die echte Gesamtzeit bei
  if (!realTotalDurations.value[activeEntry.id]) {
    // Initialisiere die Gesamtzeit, wenn sie noch nicht existiert
    realTotalDurations.value[activeEntry.id] = { ...activeEntry.total_duration }
  }

  // Berechne die echte Gesamtzeit: Startzeit bis jetzt
  const start = new Date(activeEntry.start_time)
  const now = new Date()
  const diffMs = now.getTime() - start.getTime()

  // Konvertiere die Millisekunden in Stunden, Minuten, Sekunden
  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diffMs % (1000 * 60)) / 1000)

  // Aktualisiere die Gesamtzeit des Eintrags mit der korrekten Gesamtzeit
  activeEntry.total_duration = { hours, minutes, seconds }

  // Aktualisiere unsere gespeicherte Gesamtzeit
  realTotalDurations.value[activeEntry.id] = { ...activeEntry.total_duration }

  // Effective Zeit = Gesamtzeit - Pausenzeit
  const totalSeconds =
    activeEntry.total_duration.hours * 3600 +
    activeEntry.total_duration.minutes * 60 +
    activeEntry.total_duration.seconds

  const pauseSeconds =
    activeEntry.pause_duration.hours * 3600 +
    activeEntry.pause_duration.minutes * 60 +
    activeEntry.pause_duration.seconds

  // Effektive Zeit = Gesamtzeit - Pausenzeit
  const effectiveSeconds = Math.max(0, totalSeconds - pauseSeconds)

  // Konvertiere zurück in Stunden, Minuten, Sekunden
  const effectiveHours = Math.floor(effectiveSeconds / 3600)
  const effectiveMinutes = Math.floor((effectiveSeconds % 3600) / 60)
  const effectiveSeconds2 = effectiveSeconds % 60

  activeEntry.effective_duration = {
    hours: effectiveHours,
    minutes: effectiveMinutes,
    seconds: effectiveSeconds2,
  }
}

// Watch für Timer-Updates
watch(
  globalCurrentTimer,
  () => {
    updateActiveTimeEntry()
  },
  { deep: true },
)

// Watch für Änderungen am globalen Tracking-Zustand
watch(
  globalTracking,
  (newState) => {
    // Wenn der globale Zustand sich ändert, sofort den lokalen Zustand aktualisieren
    updateLocalTimersBasedOnGlobalState()
  },
  { deep: true },
)

// Neue Funktion: Lokale Timer basierend auf dem globalen Zustand aktualisieren
function updateLocalTimersBasedOnGlobalState() {
  // Aktiven Eintrag finden, falls vorhanden
  const activeEntry = timeEntries.value.find(
    (entry) => entry.id === globalTracking.value.activeEntryId && entry.is_active,
  )

  if (!activeEntry) return

  // Status synchronisieren - ist der Eintrag pausiert oder läuft er?
  const isPaused = globalTracking.value.isPaused
  const activePause = activeEntry.pauses.find((p) => p.is_active)

  // Wenn der globale Zustand pausiert ist, aber lokal keine aktive Pause...
  if (isPaused && !activePause) {
    // Hier müssten wir die Daten neu laden, um die neue Pause zu bekommen
    fetchTimeEntries()
  }

  // Wenn der globale Zustand aktiv ist, aber lokal eine aktive Pause...
  if (!isPaused && activePause) {
    // Hier müssten wir die Daten neu laden, um die beendete Pause zu aktualisieren
    fetchTimeEntries()
  }
}

// Verbesserte Funktion für das Abrufen der Zeiteinträge
async function fetchTimeEntries() {
  loading.value = true
  error.value = null

  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/project/${props.projectId}/time-entries`)

    if (response.ok) {
      const data = await response.json()

      // Speichere den aktiven Eintrag vor dem Update, falls vorhanden
      const previousActiveEntryId = timeEntries.value.find((e) => e.is_active)?.id

      // Update die Zeiteinträge
      timeEntries.value = data.entries || []

      // Reset Pause-Timer
      currentPauseTimer.value = {}

      // Initialisiere Timer für alle aktiven Einträge und deren Pausen
      initializeTimersForActiveEntries()

      // Wenn der Fokus auf einem Eintrag lag und dieser noch existiert, wieder fokussieren
      if (expandedEntry.value) {
        const updatedExpandedEntry = timeEntries.value.find((e) => e.id === expandedEntry.value?.id)
        if (updatedExpandedEntry) {
          expandedEntry.value = updatedExpandedEntry
        } else {
          expandedEntry.value = null
        }
      }

      // Aktualisiere den Fokus auf dem aktiven Eintrag, wenn der gleiche immer noch aktiv ist
      if (previousActiveEntryId) {
        const stillActiveEntry = timeEntries.value.find(
          (e) => e.id === previousActiveEntryId && e.is_active,
        )
        if (stillActiveEntry) {
          // Expandiere den aktiven Eintrag automatisch wenn er sich verändert hat
          if (
            isEntryPaused(stillActiveEntry) !== stillActiveEntry.pauses.some((p) => p.is_active)
          ) {
            expandedEntry.value = stillActiveEntry
          }
        }
      }
    } else {
      const errorData = await response.json()
      error.value = errorData.error || 'Fehler beim Laden der Zeiteinträge'
    }
  } catch (e) {
    console.error('Fehler beim Abrufen der Zeiteinträge:', e)
    error.value = 'Ein unerwarteter Fehler ist aufgetreten. Bitte versuche es später erneut.'
  } finally {
    loading.value = false
  }
}

// Setup auto-refresh for active entries
function setupRefreshInterval() {
  // Check if there are any active entries or pauses
  const hasActiveEntries = timeEntries.value.some((entry) => entry.is_active)

  if (hasActiveEntries) {
    // Bei aktivem Timer den Eintrag sofort aktualisieren
    updateActiveTimeEntry()

    // Start pause timer for active pauses
    startPauseTimerUpdates()

    // Refresh every 30 seconds if there are active entries
    refreshInterval = window.setInterval(fetchTimeEntries, 30000)
  }
}

// Start a timer to update pause durations every second
function startPauseTimerUpdates() {
  // Clear any existing interval
  if (pauseTimerInterval) {
    clearInterval(pauseTimerInterval)
  }

  // Check if we have any active entries
  const hasActiveEntries = timeEntries.value.some((entry) => entry.is_active)

  if (hasActiveEntries) {
    // Initialisiere Gesamtzeiten für alle aktiven Einträge
    timeEntries.value.forEach((entry) => {
      if (entry.is_active) {
        updateEntryTotalDuration(entry)
      }
    })

    // Set up interval for updating timers every second
    pauseTimerInterval = window.setInterval(updatePauseTimers, 1000)
  }
}

onMounted(async () => {
  await fetchTimeEntries()
  setupRefreshInterval()
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
  if (pauseTimerInterval) {
    clearInterval(pauseTimerInterval)
  }
})
</script>

<style scoped>
.time-entries-container {
  width: 100%;
  overflow-x: auto;
}

.entries-table {
  border-radius: 0.375rem;
  overflow: hidden;
}

.entries-table table {
  width: 100%;
  border-collapse: collapse;
}

tr {
  cursor: pointer;
}
</style>
