export async function checkAuth() {
  // First check if we have a token in localStorage
  const token = localStorage.getItem('auth_token')
  if (!token) {
    return false
  }

  try {
    // Make request to auth check endpoint with the token in Authorization header
    const res = await fetch('https://chronixly.com/api/auth/check', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      credentials: 'include',
    })
    return res.ok
  } catch (e) {
    // If there's any error, consider user not authenticated
    return false
  }
}

export function getAuthToken() {
  return localStorage.getItem('auth_token')
}

export function clearAuth() {
  localStorage.removeItem('auth_token')
}
