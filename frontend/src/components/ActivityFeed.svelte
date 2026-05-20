<script>
  import { onMount } from 'svelte'
  import { apiFetch } from '../lib/api.js'

  let items = []
  let loading = false
  let error = null

  onMount(async () => {
    loading = true
    try {
      const res = await apiFetch('/activity?limit=20')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      items = await res.json()
    } catch (e) {
      error = e.message
    } finally {
      loading = false
    }
  })
</script>

<section class="activity-feed no-print" aria-label="Recent activity">
  <h3>Activity</h3>
  {#if loading}
    <p class="muted">Loading…</p>
  {:else if error}
    <p class="muted">Could not load activity.</p>
  {:else if items.length === 0}
    <p class="muted">No activity yet.</p>
  {:else}
    <ul>
      {#each items as item (item.at + item.resource)}
        <li>
          <span class="act-time">{item.at}</span>
          <strong>{item.user}</strong> {item.action} <code>{item.resource}</code>
        </li>
      {/each}
    </ul>
  {/if}
</section>

<style>
  .activity-feed {
    margin-top: 1rem;
    padding: 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    background: var(--color-surface-elevated);
  }
  .activity-feed h3 { margin: 0 0 0.5rem; font-size: 0.875rem; }
  ul { list-style: none; margin: 0; padding: 0; max-height: 10rem; overflow-y: auto; }
  li { font-size: 0.75rem; padding: 0.25rem 0; border-bottom: 1px solid var(--color-border); }
  li:last-child { border-bottom: none; }
  .act-time { color: var(--color-base-muted); margin-right: 0.35rem; }
  code { font-size: 0.7rem; }
  .muted { margin: 0; font-size: 0.8125rem; color: var(--color-base-muted); }
</style>
