<script>
  export let todos
  export let onToggle
  export let onDelete
  export let loading = false
</script>

<div class="list">
  {#if loading}
    <p class="muted">Loading…</p>
  {:else if $todos.length === 0}
    <p class="muted">No tasks yet. Add one above.</p>
  {:else}
    <ul>
      {#each $todos as todo (todo.id)}
        <li class:completed={todo.completed}>
          <label>
            <input
              type="checkbox"
              checked={todo.completed}
              on:change={() => onToggle(todo.id)}
              aria-label="Toggle {todo.title}"
            />
            <span>{todo.title}</span>
          </label>
          <button
            type="button"
            class="del"
            on:click={() => onDelete(todo.id)}
            aria-label="Delete {todo.title}"
          >×</button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .list {
    background: var(--color-surface-elevated);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
  }

  ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    border-bottom: 1px solid var(--color-border);
    gap: 0.5rem;
    transition: background var(--transition);
  }

  li:last-child {
    border-bottom: none;
  }

  li:hover {
    background: var(--color-surface);
  }

  li.completed span {
    text-decoration: line-through;
    color: var(--color-base-muted);
  }

  label {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    cursor: pointer;
    flex: 1;
    font-size: 0.9375rem;
  }

  input[type="checkbox"] {
    width: 1.125rem;
    height: 1.125rem;
    accent-color: var(--color-accent);
    cursor: pointer;
  }

  .del {
    padding: 0.35rem 0.5rem;
    background: transparent;
    border: none;
    color: var(--color-base-muted);
    font-size: 1.25rem;
    line-height: 1;
    cursor: pointer;
    border-radius: var(--radius-sm);
    transition: color var(--transition), background var(--transition);
  }

  .del:hover {
    color: var(--color-error-text);
    background: var(--color-error-bg);
  }

  .del:focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
  }

  .muted {
    margin: 0;
    padding: 1rem;
    font-size: 0.875rem;
    color: var(--color-base-muted);
    text-align: center;
  }
</style>
