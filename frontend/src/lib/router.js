/** Lightweight URL state sync (SvelteKit-style routes without migration). */

export function readRoute() {
  if (typeof window === 'undefined') return { view: 'todos', planId: null }
  const params = new URLSearchParams(window.location.search)
  const view = params.get('view') === 'oppm' ? 'oppm' : 'todos'
  return { view, planId: params.get('plan_id') }
}

export function writeRoute({ view, planId }) {
  if (typeof window === 'undefined') return
  const url = new URL(window.location.href)
  url.searchParams.set('view', view || 'todos')
  if (planId) url.searchParams.set('plan_id', planId)
  else url.searchParams.delete('plan_id')
  window.history.replaceState({}, '', url.pathname + '?' + url.searchParams.toString())
}

export function onRouteChange(handler) {
  if (typeof window === 'undefined') return () => {}
  const fn = () => handler(readRoute())
  window.addEventListener('popstate', fn)
  return () => window.removeEventListener('popstate', fn)
}
