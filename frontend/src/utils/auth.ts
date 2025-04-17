export async function checkAuth() {
  try {
    // Make request to auth check endpoint with credentials to send cookies
    const res = await fetch('https://chronixly.com/api/auth/check', {
      credentials: 'include',
    })
    return res.ok
  } catch (e) {
    return false
  }
}

export async function refreshToken() {
  try {
    // Call refresh token endpoint with credentials to send cookies
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
    const response = await fetch('https://chronixly.com/api/logout', {
      method: 'POST',
      credentials: 'include',
    })
    return response.ok
  } catch (e) {
    return false
  }
}
