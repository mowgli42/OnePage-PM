import { writable } from 'svelte/store'
import { apiFetch } from '../lib/api.js'

export const todos = writable([])
export const loading = writable(false)
export const error = writable(null)

export async function fetchTodos() {
  loading.set(true)
  error.set(null)
  try {
    const res = await apiFetch('/todos')
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    todos.set(data)
    return data
  } catch (e) {
    error.set(e.message)
    todos.set([])
    return []
  } finally {
    loading.set(false)
  }
}

export async function createTodo(title) {
  const res = await apiFetch('/todos', {
    method: 'POST',
    body: JSON.stringify({ title, completed: false }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const todo = await res.json()
  todos.update((t) => [...t, todo])
  return todo
}

export async function toggleTodo(id) {
  const list = await apiFetch('/todos').then((r) => r.json())
  const todo = list.find((t) => t.id === id)
  if (!todo) return
  const res = await apiFetch(`/todos/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ completed: !todo.completed }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const updated = await res.json()
  todos.update((t) => t.map((x) => (x.id === id ? updated : x)))
}

export async function deleteTodo(id) {
  const res = await apiFetch(`/todos/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  todos.update((t) => t.filter((x) => x.id !== id))
}
