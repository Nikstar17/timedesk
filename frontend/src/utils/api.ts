// filepath: g:\Projekte\timedesk\frontend\src\utils\api.ts

import { refreshToken } from './auth'
import { API_BASE_URL } from './config'

/**
 * Gets CSRF token from cookies
 */
function getCsrfToken(cookieName = 'csrf_access_token') {
  const cookies = document.cookie.split(';')
  for (let cookie of cookies) {
    cookie = cookie.trim()
    if (cookie.startsWith(cookieName + '=')) {
      return cookie.substring(cookieName.length + 1)
    }
  }
  return null
}

/**
 * Wrapper for fetch that handles authentication and CSRF protection
 */
export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // Clone the options to avoid modifying the original
  const requestOptions = { ...options }

  // Add headers if not present
  if (!requestOptions.headers) {
    requestOptions.headers = {}
  }

  // For methods that modify data, add the CSRF token
  const method = requestOptions.method?.toUpperCase() || 'GET'
  if (method !== 'GET' && method !== 'HEAD') {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      ;(requestOptions.headers as Record<string, string>)['X-CSRF-TOKEN'] = csrfToken
    }
  }

  // Add credentials option for cookie-based auth
  requestOptions.credentials = 'include'

  try {
    // Make the initial request
    let response = await fetch(url, requestOptions)

    // If we get a 401 with token expired message, try to refresh the token
    if (response.status === 401) {
      try {
        const errorData = await response.json()

        if (errorData.msg === 'Token has expired') {
          // Try to refresh the token
          const refreshRes = await fetch(`${API_BASE_URL}/refresh`, {
            method: 'POST',
            credentials: 'include',
            headers: {
              'X-CSRF-TOKEN': getCsrfToken('csrf_refresh_token') || '',
            },
          })

          if (refreshRes.ok) {
            // If token was refreshed successfully, retry the original request
            // Need to update the CSRF token in the headers for the retry
            if (method !== 'GET' && method !== 'HEAD') {
              const newCsrfToken = getCsrfToken()
              if (newCsrfToken) {
                ;(requestOptions.headers as Record<string, string>)['X-CSRF-TOKEN'] = newCsrfToken
              }
            }

            // Retry the original request
            return fetch(url, requestOptions)
          }
        }
      } catch (e) {
        // If we can't parse the JSON or something else goes wrong, continue with the failed response
      }
    }

    return response
  } catch (error) {
    // For network errors, log and rethrow
    console.error('API request failed:', error)
    throw error
  }
}

export const api = {
  async fetcher(url: string, options: RequestInit = {}) {
    const requestOptions = { ...options }

    if (!requestOptions.headers) {
      requestOptions.headers = {}
    }

    const method = requestOptions.method?.toUpperCase() || 'GET'
    if (method !== 'GET' && method !== 'HEAD') {
      const csrfToken = getCsrfToken()
      if (csrfToken) {
        ;(requestOptions.headers as Record<string, string>)['X-CSRF-TOKEN'] = csrfToken
      }
    }

    requestOptions.credentials = 'include'

    try {
      let response = await fetch(url, requestOptions)

      if (response.status === 401) {
        const errorData = await response.json()

        if (errorData.msg === 'Token has expired') {
          const refreshSuccess = await refreshToken()
          if (refreshSuccess) {
            const refreshRes = await fetch(`${API_BASE_URL}/refresh`, {
              method: 'POST',
              credentials: 'include',
            })

            if (refreshRes.ok) {
              const newCsrfToken = getCsrfToken()
              if (newCsrfToken) {
                ;(requestOptions.headers as Record<string, string>)['X-CSRF-TOKEN'] = newCsrfToken
              }

              return fetch(url, requestOptions)
            }
          }
        }
      }

      return response
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  },
}
