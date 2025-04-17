import { ref } from 'vue'
import { API_BASE_URL } from './config'

/**
 * Gets CSRF token from cookies
 */
function getCsrfToken(cookieName = 'csrf_refresh_token') {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    cookie = cookie.trim()
    if (cookie.startsWith(cookieName + '=')) {
      return cookie.substring(cookieName.length + 1)
    }
  }
  return null
}

export const isAuthenticated = ref(false)
export const isAdmin = ref(false)
export const userFullName = ref('')

export async function checkAuthStatus() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/check`, {
      method: 'GET',
      credentials: 'include',
    })

    // If the check fails, try to automatically refresh the token
    if (!res.ok) {
      const data = await res.json()
      if (data.msg === 'Token has expired') {
        // Try to refresh the token
        return await refreshToken()
      }
      return false
    }

    return true
  } catch (e) {
    return false
  }
}

export async function refreshToken() {
  try {
    // Get CSRF token from cookies
    const csrfToken = getCsrfToken('csrf_refresh_token')

    // Call refresh token endpoint with the CSRF token in headers
    const refreshRes = await fetch(`${API_BASE_URL}/refresh`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-TOKEN': csrfToken || '',
      },
    })

    return refreshRes.ok
  } catch (e) {
    return false
  }
}

export async function logout() {
  try {
    // Get CSRF token from cookies
    const csrfToken = getCsrfToken('csrf_access_token')

    // Use correct logout endpoint with CSRF token
    const response = await fetch(`${API_BASE_URL}/logout`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-TOKEN': csrfToken || '',
      },
    })
    return response.ok
  } catch (e) {
    return false
  }
}
