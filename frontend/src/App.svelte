<script>
  import { onMount } from 'svelte'
  import { todos, loading, error, fetchTodos, createTodo, toggleTodo, deleteTodo } from './stores/todos.js'
  import { oppmEditing, plansList, currentPlanId, fetchPlans, fetchPlan, initPlanFromUrl } from './stores/plan.js'
  import { fetchAuthMe } from './stores/auth.js'
  import { canWrite } from './stores/auth.js'
  import TodoList from './components/TodoList.svelte'
  import TodoForm from './components/TodoForm.svelte'
  import OPPMPage from './components/OPPMPage.svelte'
  import LoginPanel from './components/LoginPanel.svelte'
  import KanbanBoard from './components/KanbanBoard.svelte'

  function getViewFromUrl() {
    const params = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '')
    const v = params.get('view')
    return v === 'oppm' ? 'oppm' : 'todos'
  }

  let view = getViewFromUrl()
  let todoLayout = 'list'
  let darkMode = false

  function setView(v) {
    view = v
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href)
      url.searchParams.set('view', v)
      window.history.replaceState({}, '', url.pathname + '?' + url.searchParams.toString())
    }
    if (v === 'oppm') fetchPlans().then(() => fetchPlan($currentPlanId))
  }

  function toggleDark() {
    darkMode = !darkMode
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.theme = darkMode ? 'dark' : 'light'
      localStorage.setItem('pm_theme', darkMode ? 'dark' : 'light')
    }
  }

  onMount(() => {
    const saved = localStorage.getItem('pm_theme')
    darkMode = saved === 'dark'
    document.documentElement.dataset.theme = darkMode ? 'dark' : 'light'
    fetchAuthMe()
    fetchTodos()
    const planId = initPlanFromUrl()
    if (planId) currentPlanId.set(planId)
    if (view === 'oppm') fetchPlans().then(() => fetchPlan(planId || $currentPlanId))
    const onPopState = () => { view = getViewFromUrl() }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  })
</script>

<svelte:head>
  <!-- Design system v2.0: refined editorial -->
</svelte:head>

<main class="app" class:print-oppm={view === 'oppm'}>
  <header class="app-header">
    <h1>Project Management</h1>
    {#if view === 'oppm' && $plansList.length > 0}
      <div class="plan-select-wrap">
        <label for="plan-select" class="visually-hidden">Plan</label>
        <select
          id="plan-select"
          class="plan-select"
          bind:value={$currentPlanId}
          on:change={() => fetchPlan($currentPlanId)}
          aria-label="Select plan"
        >
          {#each $plansList as p}
            <option value={p.id}>{p.title}</option>
          {/each}
        </select>
      </div>
    {/if}
    <span class="subtitle">Todo tracker & OPPM</span>
    <div class="tabs" role="tablist" aria-label="View">
      <button class="tab" class:active={view === 'todos'} on:click={() => setView('todos')} role="tab" aria-selected={view === 'todos'}>Todos</button>
      <button class="tab" class:active={view === 'oppm'} on:click={() => setView('oppm')} role="tab" aria-selected={view === 'oppm'}>OPPM</button>
    </div>
    <LoginPanel />
    <button type="button" class="header-icon theme-toggle" on:click={toggleDark} aria-label="Toggle dark mode" title="Toggle theme">
      {darkMode ? '☀' : '☾'}
    </button>
    {#if view === 'oppm'}
      <button type="button" class="header-icon" on:click={() => window.print()} aria-label="Print one page" title="Print one page">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 9V2h12v7"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/></svg>
      </button>
      <button type="button" class="header-icon" on:click={() => oppmEditing.set(true)} aria-label="Edit plan" title="Edit plan">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
      </button>
    {/if}
  </header>

  <section class="app-content">
    {#if view === 'oppm'}
      <OPPMPage />
    {:else}
      {#if $error}
        <div class="error" role="alert">Backend offline: {$error}. Start with <code>uvicorn main:app --reload</code> in backend/</div>
      {/if}
      <div class="todo-layout-tabs no-print">
        <button type="button" class:active={todoLayout === 'list'} on:click={() => (todoLayout = 'list')}>List</button>
        <button type="button" class:active={todoLayout === 'kanban'} on:click={() => (todoLayout = 'kanban')}>Kanban</button>
      </div>
      {#if canWrite()}
        <TodoForm onSubmit={(title) => createTodo(title)} />
      {/if}
      {#if todoLayout === 'kanban'}
        <KanbanBoard {todos} onToggle={toggleTodo} onDelete={deleteTodo} loading={$loading} />
      {:else}
        <TodoList {todos} onToggle={toggleTodo} onDelete={deleteTodo} loading={$loading} />
      {/if}
    {/if}
  </section>
</main>

<style>
  :global(html) {
    --font-display: 'Fraunces', Georgia, serif;
    --font-body: 'Source Sans 3', system-ui, sans-serif;
    --color-base: #1f2937;
    --color-base-muted: #6b7280;
    --color-surface: #f9fafb;
    --color-surface-elevated: #ffffff;
    --color-border: #e5e7eb;
    --color-border-strong: #9ca3af;
    --color-accent: #e85d4c;
    --color-accent-hover: #dc2626;
    --color-accent-muted: #fef2f2;
    --color-secondary: #0d9488;
    --color-secondary-hover: #0f766e;
    --color-secondary-muted: #f0fdfa;
    --color-error-bg: #fef2f2;
    --color-error-border: #fecaca;
    --color-error-text: #991b1b;
    --color-success: #059669;
    --color-warn: #d97706;
    --color-done: var(--color-secondary);
    --color-risk: var(--color-accent);
    --color-planned: var(--color-base-muted);
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 10px;
    --shadow-sm: 0 1px 2px rgba(31, 41, 55, 0.06);
    --shadow-md: 0 2px 8px rgba(31, 41, 55, 0.08);
    --transition: 0.2s ease;
  }
  :global(html[data-theme='dark']) {
    --color-base: #f3f4f6;
    --color-base-muted: #9ca3af;
    --color-surface: #111827;
    --color-surface-elevated: #1f2937;
    --color-border: #374151;
    --color-border-strong: #6b7280;
    --color-accent-muted: #451a1a;
    --color-secondary-muted: #134e4a;
    --color-error-bg: #450a0a;
    --color-error-border: #7f1d1d;
    --color-error-text: #fecaca;
  }
  .todo-layout-tabs {
    display: inline-flex;
    gap: 0.25rem;
    margin-bottom: 0.5rem;
  }
  .todo-layout-tabs button {
    padding: 0.25rem 0.6rem;
    font-size: 0.75rem;
    border: 1px solid var(--color-border);
    background: var(--color-surface-elevated);
    border-radius: var(--radius-sm);
    cursor: pointer;
  }
  .todo-layout-tabs button.active {
    background: var(--color-accent-muted);
    border-color: var(--color-accent);
    color: var(--color-accent);
  }
  .theme-toggle { font-size: 1.1rem; }

  .app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0;
    font-family: var(--font-body);
    font-size: 0.9375rem;
    line-height: 1.5;
    color: var(--color-base);
    background: var(--color-surface);
    min-height: 100vh;
  }

  /* Compact, top-anchored header: single row */
  .app-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;
    padding: 0.5rem 1.25rem 0.5rem 1.25rem;
    background: var(--color-surface-elevated);
    border-bottom: 1px solid var(--color-border);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  h1 {
    margin: 0;
    font-family: var(--font-display);
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--color-base);
  }

  .plan-select-wrap {
    display: inline-flex;
    align-items: center;
  }
  .plan-select {
    padding: 0.3rem 1.75rem 0.3rem 0.5rem;
    font-family: var(--font-body);
    font-size: 0.8125rem;
    color: var(--color-base);
    background: var(--color-surface-elevated);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    cursor: pointer;
    max-width: 16rem;
  }
  .plan-select:hover { border-color: var(--color-border-strong); }
  .plan-select:focus {
    outline: none;
    border-color: var(--color-accent);
    box-shadow: 0 0 0 2px var(--color-accent-muted);
  }
  .visually-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
  .subtitle {
    font-size: 0.8125rem;
    color: var(--color-base-muted);
    margin-right: auto;
  }

  .tabs {
    display: inline-flex;
    gap: 0;
    padding: 0.2rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
  }

  .tab {
    padding: 0.35rem 0.875rem;
    font-family: var(--font-body);
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--color-base-muted);
    background: transparent;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: color var(--transition), background var(--transition);
  }

  .tab:hover {
    color: var(--color-base);
    background: var(--color-surface-elevated);
  }

  .tab.active {
    color: var(--color-accent);
    background: var(--color-accent-muted);
    font-weight: 600;
  }

  .tab:focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
  }

  .header-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    padding: 0;
    color: var(--color-base-muted);
    background: transparent;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: color var(--transition), background var(--transition);
  }
  .header-icon svg {
    width: 1.5rem;
    height: 1.5rem;
  }
  .header-icon:hover {
    color: var(--color-accent);
    background: var(--color-accent-muted);
  }
  .header-icon:focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
  }

  .app-content {
    padding: 0.75rem 1.25rem 1.25rem;
  }

  .error {
    padding: 0.625rem 0.875rem;
    background: var(--color-error-bg);
    border: 1px solid var(--color-error-border);
    border-radius: var(--radius-md);
    color: var(--color-error-text);
    font-size: 0.875rem;
    margin-bottom: 0.75rem;
  }

  .error code {
    background: #fee2e2;
    padding: 0.1em 0.3em;
    border-radius: 4px;
    font-size: 0.875em;
  }

  @media print {
    @page { size: A4 landscape; margin: 12mm; }
    .print-oppm .app-header { display: none !important; }
    .print-oppm .app-content { padding: 0; }
    .print-oppm { padding: 0; max-width: none; }
  }
</style>
