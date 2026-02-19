<script>
  import { onMount } from 'svelte'
  import { todos, loading, error, fetchTodos, createTodo, toggleTodo, deleteTodo } from './stores/todos.js'
  import TodoList from './components/TodoList.svelte'
  import TodoForm from './components/TodoForm.svelte'

  onMount(() => fetchTodos())
</script>

<main class="app">
  <header>
    <h1>Project Management</h1>
    <p class="subtitle">One-page todo tracker</p>
  </header>

  {#if $error}
    <div class="error">Backend offline: {$error}. Start with <code>uvicorn main:app --reload</code> in backend/</div>
  {/if}

  <TodoForm onSubmit={(title) => createTodo(title)} />
  <TodoList {todos} onToggle={toggleTodo} onDelete={deleteTodo} loading={$loading} />
</main>

<style>
  .app {
    max-width: 480px;
    margin: 0 auto;
    padding: 2rem;
    font-family: system-ui, -apple-system, sans-serif;
  }
  h1 {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 600;
  }
  .subtitle {
    margin: 0.25rem 0 1.5rem;
    color: #64748b;
    font-size: 0.95rem;
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
