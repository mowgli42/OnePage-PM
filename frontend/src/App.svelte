<script>
  import { onMount } from 'svelte'
  import { todos, loading, error, fetchTodos, createTodo, toggleTodo, deleteTodo } from './stores/todos.js'
  import TodoList from './components/TodoList.svelte'
  import TodoForm from './components/TodoForm.svelte'
  import OPPMPage from './components/OPPMPage.svelte'

  let view = 'todos'

  onMount(() => fetchTodos())
</script>

<main class="app">
  <header>
    <h1>Project Management</h1>
    <p class="subtitle">One-page todo tracker & OPPM</p>
    <div class="tabs">
      <button class="tab" class:active={view === 'todos'} on:click={() => view = 'todos'}>Todos</button>
      <button class="tab" class:active={view === 'oppm'} on:click={() => view = 'oppm'}>OPPM</button>
    </div>
  </header>

  {#if view === 'oppm'}
    <OPPMPage />
  {:else}
    {#if $error}
      <div class="error">Backend offline: {$error}. Start with <code>uvicorn main:app --reload</code> in backend/</div>
    {/if}

    <TodoForm onSubmit={(title) => createTodo(title)} />
    <TodoList {todos} onToggle={toggleTodo} onDelete={deleteTodo} loading={$loading} />
  {/if}
</main>

<style>
  .app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    font-family: system-ui, -apple-system, sans-serif;
  }
  .app:has(.oppm) { max-width: 1200px; }
  h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 600;
  }
  .subtitle {
    margin: 0.25rem 0 0.5rem;
    color: #64748b;
    font-size: 0.95rem;
  }
  .tabs {
    display: flex;
    gap: 0.25rem;
    margin: 1rem 0 1.5rem;
  }
  .tab {
    padding: 0.5rem 1rem;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
  }
  .tab:hover { background: #e2e8f0; }
  .tab.active {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
  }
  .error {
    padding: 0.75rem 1rem;
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    color: #991b1b;
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }
  .error code {
    background: #fee2e2;
    padding: 0.1em 0.3em;
    border-radius: 4px;
  }
</style>
