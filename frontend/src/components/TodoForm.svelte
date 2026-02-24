<script>
  import { createEventDispatcher } from 'svelte'
  export let onSubmit

  let title = ''

  function handleSubmit() {
    const t = title.trim()
    if (!t) return
    onSubmit(t)
    title = ''
  }
</script>

<form on:submit|preventDefault={handleSubmit} class="form">
  <input
    type="text"
    bind:value={title}
    placeholder="Add a task..."
    maxlength="200"
    class="input"
    aria-label="New task title"
  />
  <button type="submit" class="btn" disabled={!title.trim()}>Add</button>
</form>

<style>
  .form {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .input {
    flex: 1;
    padding: 0.5rem 0.75rem;
    font-size: 0.9375rem;
    font-family: var(--font-body);
    font-size: 1rem;
    color: var(--color-base);
    background: var(--color-surface-elevated);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    transition: border-color var(--transition), box-shadow var(--transition);
  }

  .input::placeholder {
    color: var(--color-base-muted);
  }

  .input:hover {
    border-color: var(--color-border-strong);
  }

  .input:focus {
    outline: none;
    border-color: var(--color-accent);
    box-shadow: 0 0 0 3px var(--color-accent-muted);
  }

  .btn {
    padding: 0.5rem 1rem;
    font-family: var(--font-body);
    font-size: 0.875rem;
    font-weight: 600;
    color: white;
    background: var(--color-accent);
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: background var(--transition), transform 0.15s ease;
  }

  .btn:hover:not(:disabled) {
    background: var(--color-accent-hover);
  }

  .btn:active:not(:disabled) {
    transform: scale(0.98);
  }

  .btn:focus-visible {
    outline: 2px solid var(--color-accent);
    outline-offset: 2px;
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
