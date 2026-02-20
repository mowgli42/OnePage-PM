import { writable } from 'svelte/store'

const API = 'http://localhost:8000'

export const todos = writable([])
export const loading = writable(false)
export const error = writable(null)

export async function fetchTodos() {
  loading.set(true)
  error.set(null)
  try {
    const res = await fetch(`${API}/todos`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    todos.set(data)
  } catch (e) {
    error.set(e.message)
  } finally {
    loading.set(false)
  }
}

export async function createTodo(title) {
  const res = await fetch(`${API}/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, completed: false }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const todo = await res.json()
  todos.update((t) => [...t, todo])
}

export async function toggleTodo(id) {
  const list = await fetch(`${API}/todos`).then((r) => r.json())
  const todo = list.find((t) => t.id === id)
  if (!todo) return
  const res = await fetch(`${API}/todos/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ completed: !todo.completed }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const updated = await res.json()
  todos.update((t) => t.map((x) => (x.id === id ? updated : x)))
}

export async function deleteTodo(id) {
  const res = await fetch(`${API}/todos/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  todos.update((t) => t.filter((x) => x.id !== id))
}
