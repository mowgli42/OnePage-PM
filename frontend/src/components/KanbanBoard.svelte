<script>
  export let todos
  export let onToggle
  export let onDelete
  export let loading = false

  $: pending = $todos.filter((t) => !t.completed)
  $: done = $todos.filter((t) => t.completed)
</script>

<div class="kanban">
  <div class="kanban-col">
    <h3>To do <span class="count">{pending.length}</span></h3>
    {#if loading}
      <p class="muted">Loading…</p>
    {:else if pending.length === 0}
      <p class="muted">No open tasks</p>
    {:else}
      {#each pending as todo (todo.id)}
        <article class="kanban-card">
          <label><input type="checkbox" on:change={() => onToggle(todo.id)} /> {todo.title}</label>
          <button type="button" class="del" on:click={() => onDelete(todo.id)} aria-label="Delete">×</button>
        </article>
      {/each}
    {/if}
  </div>
  <div class="kanban-col done-col">
    <h3>Done <span class="count">{done.length}</span></h3>
    {#each done as todo (todo.id)}
      <article class="kanban-card done">
        <label><input type="checkbox" checked on:change={() => onToggle(todo.id)} /> <span class="strike">{todo.title}</span></label>
        <button type="button" class="del" on:click={() => onDelete(todo.id)} aria-label="Delete">×</button>
      </article>
    {/each}
  </div>
</div>

<style>
  .kanban {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-top: 0.75rem;
  }
  @media (max-width: 640px) {
    .kanban { grid-template-columns: 1fr; }
  }
  .kanban-col {
    background: var(--color-surface-elevated);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 0.75rem;
    min-height: 8rem;
  }
  .kanban-col h3 { margin: 0 0 0.5rem; font-size: 0.875rem; }
  .count { color: var(--color-base-muted); font-weight: 400; }
  .kanban-card {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.5rem;
    margin-bottom: 0.35rem;
    background: var(--color-surface);
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
  }
  .kanban-card label { flex: 1; cursor: pointer; }
  .strike { text-decoration: line-through; color: var(--color-base-muted); }
  .del {
    background: none;
    border: none;
    color: var(--color-base-muted);
    cursor: pointer;
    font-size: 1.1rem;
    line-height: 1;
  }
  .muted { font-size: 0.8125rem; color: var(--color-base-muted); margin: 0; }
</style>
