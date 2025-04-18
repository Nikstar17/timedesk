<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h2 class="text-2xl font-bold mb-6 text-center">Login to Chronixly</h2>

      <div
        v-if="error"
        class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
      >
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
            Username
          </label>
          <input
            v-model="email"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="username"
            type="text"
            placeholder="Username"
            required
          />
        </div>

        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
            Password
          </label>
          <input
            v-model="password"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            placeholder="Password"
            required
          />
        </div>

        <div class="flex items-center justify-between">
          <button
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full"
            type="submit"
            :disabled="isLoading"
          >
            {{ isLoading ? 'Logging in...' : 'Login' }}
          </button>
        </div>

        <div class="mt-4 text-center">
          <router-link to="/register" class="text-blue-500 hover:text-blue-700">
            Noch kein Konto? Hier registrieren
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

const email = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)
const router = useRouter()

async function handleLogin() {
  isLoading.value = true
  error.value = ''

  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Wichtig für Cookie-basierte Authentifizierung
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Login failed')
    }

    // Bei Cookie-basierter Authentifizierung müssen wir den Token nicht
    // in localStorage speichern, da er in den Cookies gespeichert wird
    router.push('/')
  } catch (err: any) {
    error.value = err.message || 'An error occurred during login'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped></style>
