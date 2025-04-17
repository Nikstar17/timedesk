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

export async function checkAuth() {
  try {
    // Make request to auth check endpoint with credentials to send cookies
    const res = await fetch('https://chronixly.com/api/auth/check', {
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
    const refreshRes = await fetch('https://chronixly.com/api/refresh', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-TOKEN': csrfToken || '', // Include CSRF token in header
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
    const response = await fetch('https://chronixly.com/api/logout', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'X-CSRF-TOKEN': csrfToken || '', // Include CSRF token in header
      },
    })
    return response.ok
  } catch (e) {
    return false
  }
}
