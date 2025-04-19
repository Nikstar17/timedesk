<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">Registrierung bei TimeDesk</h2>

      <div
        v-if="error"
        class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
      >
        {{ error }}
      </div>

      <div
        v-if="success"
        class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"
      >
        {{ success }}
      </div>

      <form @submit.prevent="handleRegistration">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="name"> Name </label>
          <input
            v-model="name"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="name"
            type="text"
            placeholder="Vollständiger Name"
            required
          />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="email"> E-Mail </label>
          <input
            v-model="email"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="email"
            type="email"
            placeholder="E-Mail-Adresse"
            required
          />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
            Passwort
          </label>
          <input
            v-model="password"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            placeholder="Passwort"
            required
          />
        </div>

        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="confirmPassword">
            Passwort bestätigen
          </label>
          <input
            v-model="confirmPassword"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="confirmPassword"
            type="password"
            placeholder="Passwort wiederholen"
            required
          />
        </div>

        <div class="flex items-center justify-between">
          <button
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
            type="submit"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Registrierung läuft...' : 'Registrieren' }}
          </button>
        </div>

        <div class="mt-4 text-center">
          <router-link to="/login" class="text-blue-500 hover:text-blue-700">
            Bereits registriert? Hier anmelden
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '@/utils/config'

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const success = ref('')
const isLoading = ref(false)
const router = useRouter()

async function handleRegistration() {
  // Zurücksetzen der Meldungen
  error.value = ''
  success.value = ''

  // Validierung
  if (password.value !== confirmPassword.value) {
    error.value = 'Die Passwörter stimmen nicht überein'
    return
  }

  if (password.value.length < 6) {
    error.value = 'Das Passwort muss mindestens 6 Zeichen lang sein'
    return
  }

  isLoading.value = true

  try {
    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        name: name.value,
        email: email.value,
        password: password.value,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Registrierung fehlgeschlagen')
    }

    // Erfolgsmeldung anzeigen
    success.value = 'Registrierung erfolgreich! Sie werden zur Anmeldeseite weitergeleitet...'

    // Formulardaten zurücksetzen
    name.value = ''
    email.value = ''
    password.value = ''
    confirmPassword.value = ''

    // Nach kurzer Verzögerung zur Login-Seite weiterleiten
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err: any) {
    error.value = err.message || 'Bei der Registrierung ist ein Fehler aufgetreten'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped></style>
