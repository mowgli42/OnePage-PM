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
            />
            <span>{todo.title}</span>
          </label>
          <button
            type="button"
            class="del"
            on:click={() => onDelete(todo.id)}
            aria-label="Delete"
          >×</button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .list {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
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
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    gap: 0.5rem;
  }
  li:last-child {
    border-bottom: none;
  }
  li.completed span {
    text-decoration: line-through;
    color: #94a3b8;
  }
  label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    flex: 1;
  }
  input[type="checkbox"] {
    width: 1.1em;
    height: 1.1em;
    accent-color: #2563eb;
  }
  .del {
    padding: 0.25rem 0.5rem;
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 1.25rem;
    cursor: pointer;
    line-height: 1;
  }
  .del:hover {
    color: #dc2626;
  }
  .muted {
    margin: 0;
    padding: 1.5rem;
    color: #94a3b8;
    text-align: center;
  }
</style>
