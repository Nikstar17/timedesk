export async function checkAuth() {
  try {
    const res = await fetch('/auth/check', {
      credentials: 'include',
    })
    return res.ok
  } catch (e) {
    return false
  }
}
