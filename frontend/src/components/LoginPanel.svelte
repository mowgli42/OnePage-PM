<script>
  import { authUser, authError, authLoading, login, logout, fetchAuthMe } from '../stores/auth.js'
  import { onMount } from 'svelte'

  let username = 'admin'
  let password = ''
  let showLogin = false

  onMount(() => fetchAuthMe())

  $: needsLogin = $authUser?.auth_enabled && !$authUser?.username
  $: showPanel = showLogin || needsLogin
</script>

{#if $authUser?.auth_enabled}
  <div class="auth-bar no-print">
    {#if $authUser?.username && $authUser.username !== 'anonymous'}
      <span class="auth-user">{$authUser.username} ({$authUser.role})</span>
      <button type="button" class="btn-link" on:click={logout}>Log out</button>
    {:else}
      <button type="button" class="btn-link" on:click={() => (showLogin = true)}>Log in</button>
    {/if}
  </div>
{/if}

{#if showPanel}
  <div class="login-overlay no-print" role="dialog" aria-label="Login">
    <form
      class="login-card"
      on:submit|preventDefault={async () => {
        await login(username, password)
        showLogin = false
      }}
    >
      <h2>Sign in</h2>
      <p class="hint">Admin can edit; guest is read-only when auth is enabled.</p>
      {#if $authError}
        <p class="error" role="alert">{$authError}</p>
      {/if}
      <label>
        Username
        <input type="text" bind:value={username} autocomplete="username" required />
      </label>
      <label>
        Password
        <input type="password" bind:value={password} autocomplete="current-password" required />
      </label>
      <div class="login-actions">
        <button type="submit" disabled={$authLoading}>{$authLoading ? 'Signing in…' : 'Sign in'}</button>
        {#if !needsLogin}
          <button type="button" class="btn-secondary" on:click={() => (showLogin = false)}>Cancel</button>
        {/if}
      </div>
    </form>
  </div>
{/if}

<style>
  .auth-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: var(--color-base-muted);
  }
  .btn-link {
    background: none;
    border: none;
    color: var(--color-accent);
    cursor: pointer;
    font-size: inherit;
    padding: 0;
  }
  .login-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }
  .login-card {
    background: var(--color-surface-elevated);
    padding: 1.5rem;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    width: min(22rem, 92vw);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  .login-card h2 { margin: 0; font-family: var(--font-display); font-size: 1.25rem; }
  .hint { margin: 0; font-size: 0.8125rem; color: var(--color-base-muted); }
  .error { margin: 0; color: var(--color-error-text); font-size: 0.875rem; }
  label { display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8125rem; }
  input {
    padding: 0.4rem 0.5rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font: inherit;
  }
  .login-actions { display: flex; gap: 0.5rem; margin-top: 0.25rem; }
  button[type='submit'] {
    padding: 0.4rem 0.875rem;
    background: var(--color-accent);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
  }
  .btn-secondary {
    padding: 0.4rem 0.875rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    cursor: pointer;
  }
</style>
