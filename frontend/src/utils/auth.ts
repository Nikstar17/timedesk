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
    // Call refresh token endpoint - using the correct path from backend
    const refreshRes = await fetch('https://chronixly.com/api/refresh', {
      method: 'POST',
      credentials: 'include',
    })

    return refreshRes.ok
  } catch (e) {
    return false
  }
}

export async function logout() {
  try {
    // Use correct logout endpoint from the backend
    const response = await fetch('https://chronixly.com/api/logout', {
      method: 'POST',
      credentials: 'include',
    })
    return response.ok
  } catch (e) {
    return false
  }
}
