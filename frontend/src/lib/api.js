const API = '/_/backend'

export function getAuthToken() {
  if (typeof localStorage === 'undefined') return null
  return localStorage.getItem('pm_auth_token')
}

export function setAuthToken(token) {
  if (token) localStorage.setItem('pm_auth_token', token)
  else localStorage.removeItem('pm_auth_token')
}

export async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  const token = getAuthToken()
  if (token) headers.Authorization = `Bearer ${token}`
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }
  const res = await fetch(`${API}${path}`, { ...options, headers })
  if (res.status === 401) {
    setAuthToken(null)
    throw new Error('Authentication required')
  }
  return res
}

export { API }
