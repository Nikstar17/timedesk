<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted, onUnmounted, provide } from 'vue'
import { API_BASE_URL } from './utils/config'
import { fetchWithAuth } from './utils/api'

// Create a globally accessible state for active time tracking
const isTimeTrackingActive = ref(false)
const activeTimeEntryId = ref<string | null>(null)
const showCloseConfirmationDialog = ref(false)
const userWantsToClose = ref(false)

// Provide these states to all child components
provide('isTimeTrackingActive', isTimeTrackingActive)
provide('showCloseConfirmationDialog', showCloseConfirmationDialog)

// Function to check if there's an active time entry
async function checkActiveTimeTracking() {
  try {
    // Only check if the user is logged in (has an auth token)
    const token = localStorage.getItem('auth_token')
    if (!token) return false

    const response = await fetchWithAuth(`${API_BASE_URL}/active-time-entry`)

    if (response.ok) {
      const data = await response.json()

      if (data.active_entry) {
        isTimeTrackingActive.value = true
        activeTimeEntryId.value = data.active_entry.id
        return true
      }
    }

    isTimeTrackingActive.value = false
    activeTimeEntryId.value = null
    return false
  } catch (e) {
    console.error('Error checking active time entry:', e)
    return false
  }
}

// Cancel the page close action
function cancelClosePage() {
  showCloseConfirmationDialog.value = false
  userWantsToClose.value = false
}

// Continue with page close action
async function continueClosePage(stopTimer: boolean) {
  if (stopTimer && activeTimeEntryId.value) {
    try {
      await fetchWithAuth(`${API_BASE_URL}/stop-time-entry`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          time_entry_id: activeTimeEntryId.value,
        }),
      })
      isTimeTrackingActive.value = false
    } catch (e) {
      console.error('Error stopping time entry:', e)
    }
  }

  // Allow the browser to proceed with closing
  userWantsToClose.value = true
  showCloseConfirmationDialog.value = false

  // Create a small delay before allowing the closure to ensure the tracking is stopped
  setTimeout(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload)
    // Attempt to close the page programmatically
    window.close()
    // If window.close() doesn't work (common in modern browsers),
    // the user will need to confirm the native browser dialog
  }, 300)
}

// Set up the beforeunload event handler with the custom dialog
const handleBeforeUnload = (event: BeforeUnloadEvent) => {
  // Only show confirmation if time tracking is active and user hasn't already confirmed
  if (isTimeTrackingActive.value && !userWantsToClose.value) {
    // Show our custom dialog instead of letting the browser show its dialog
    showCloseConfirmationDialog.value = true

    // Prevent immediate closure to show our custom dialog
    event.preventDefault()
    event.returnValue = '' // Browsers will ignore this text but require the property to be set
    return ''
  }
}

function setupGlobalBeforeUnloadHandler() {
  // Add the event listener
  window.addEventListener('beforeunload', handleBeforeUnload)

  // Remove the event listener when component is unmounted
  onUnmounted(() => {
    window.removeEventListener('beforeunload', handleBeforeUnload)
  })
}

onMounted(() => {
  // Check for active time tracking when the app loads
  checkActiveTimeTracking()

  // Set up global handler
  setupGlobalBeforeUnloadHandler()

  // We don't need to periodically check for active time tracking
  // This will be managed by the ShowProjects component when the time tracking state changes
  // The global state is updated via the inject/provide mechanism when actions happen
})
</script>

<template>
  <main>
    <RouterView />

    <!-- Custom confirmation dialog for page close with active time tracking -->
    <div
      v-if="showCloseConfirmationDialog"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Aktive Zeiterfassung</h3>
        <p class="mb-6">
          Es läuft noch eine aktive Zeiterfassung. Möchtest du die Erfassung stoppen oder
          weiterlaufen lassen?
        </p>
        <div class="flex justify-end space-x-3">
          <button
            @click="cancelClosePage"
            class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
          >
            Abbrechen
          </button>
          <button
            @click="continueClosePage(false)"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Weiterlaufen lassen
          </button>
          <button
            @click="continueClosePage(true)"
            class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Stoppen & Verlassen
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped></style>
