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
  />
  <button type="submit" class="btn" disabled={!title.trim()}>Add</button>
</form>

<style>
  .form {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  .input {
    flex: 1;
    padding: 0.6rem 0.75rem;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
  }
  .input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
  .btn {
    padding: 0.6rem 1rem;
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
  }
  .btn:hover:not(:disabled) {
    background: #1d4ed8;
  }
  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
