import { writable, get } from 'svelte/store'
import { apiFetch, setAuthToken, getAuthToken } from '../lib/api.js'

export const authUser = writable(null)
export const authError = writable(null)
export const authLoading = writable(false)

export async function fetchAuthMe() {
  authLoading.set(true)
  authError.set(null)
  try {
    const res = await apiFetch('/auth/me')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (data.auth_enabled === false) {
      authUser.set({ username: 'local', role: 'admin', auth_enabled: false })
    } else {
      authUser.set({ ...data, auth_enabled: true })
    }
    return data
  } catch (e) {
    authError.set(e.message)
    authUser.set(null)
    return null
  } finally {
    authLoading.set(false)
  }
}

export async function login(username, password) {
  authLoading.set(true)
  authError.set(null)
  try {
    const res = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${res.status}`)
    }
    const data = await res.json()
    setAuthToken(data.token)
    authUser.set({ username: data.username, role: data.role, auth_enabled: true })
    return data
  } catch (e) {
    authError.set(e.message)
    throw e
  } finally {
    authLoading.set(false)
  }
}

export function logout() {
  setAuthToken(null)
  authUser.set(null)
}

export function canWrite() {
  const u = get(authUser)
  if (!u) return true
  if (u.auth_enabled === false) return true
  return u.role === 'admin'
}
