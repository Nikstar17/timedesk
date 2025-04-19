<template>
  <div class="h-10 w-full bg-gray-100 flex justify-end items-center px-4">
    <button @click="handleLogout" class="text-red-600 hover:text-red-800 transition-colors">
      Logout
    </button>
  </div>

  <!-- Confirmation Dialog for Active Time Tracking -->
  <div
    v-if="showLogoutConfirmation"
    class="fixed inset-0 bg-black/50 bg-opacity-50 flex items-center justify-center z-50"
  >
    <div class="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
      <h3 class="text-xl font-bold mb-4">Aktive Zeiterfassung</h3>
      <p class="mb-6">
        Es läuft noch eine aktive Zeiterfassung. Möchtest du die Erfassung stoppen oder weiterlaufen
        lassen?
      </p>
      <div class="flex justify-end space-x-3">
        <button
          @click="cancelLogout"
          class="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 transition-colors"
        >
          Abbrechen
        </button>
        <button
          @click="continueLogout(false)"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Weiterlaufen lassen
        </button>
        <button
          @click="continueLogout(true)"
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Stoppen & Logout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { logout } from '@/utils/auth'
import { API_BASE_URL } from '@/utils/config'
import { fetchWithAuth } from '@/utils/api'

const router = useRouter()
const showLogoutConfirmation = ref(false)
const isTimeTrackingActive = ref(false)
const activeTimeEntryId = ref<string | null>(null)

async function checkActiveTimeTracking() {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/active-time-entry`)

    if (response.ok) {
      const data = await response.json()

      if (data.active_entry) {
        isTimeTrackingActive.value = true
        activeTimeEntryId.value = data.active_entry.id
        return true
      }
    }

    return false
  } catch (e) {
    console.error('Error checking active time entry:', e)
    return false
  }
}

async function handleLogout() {
  const hasActiveTracking = await checkActiveTimeTracking()

  if (hasActiveTracking) {
    showLogoutConfirmation.value = true
  } else {
    // No active tracking, proceed with logout
    proceedWithLogout()
  }
}

function cancelLogout() {
  showLogoutConfirmation.value = false
}

async function continueLogout(stopTimer: boolean) {
  showLogoutConfirmation.value = false

  if (stopTimer && activeTimeEntryId.value) {
    // Stop the timer before logging out
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
    } catch (e) {
      console.error('Error stopping time entry:', e)
    }
  }

  // Proceed with logout
  proceedWithLogout()
}

async function proceedWithLogout() {
  const success = await logout()
  if (success) {
    router.push('/login')
  }
}
</script>

<style scoped></style>
