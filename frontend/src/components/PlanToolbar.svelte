<script>
  import { currentPlanId, planSearch, fetchPlans, createPlan, deletePlan, duplicatePlan, plan, savePlan } from '../stores/plan.js'
  import { canWrite } from '../stores/auth.js'
  import { get } from 'svelte/store'

  let newTitle = 'New Project'
  let importInput

  async function onSearchInput(e) {
    planSearch.set(e.target.value)
    await fetchPlans(e.target.value)
  }

  async function handleNew() {
    await createPlan(newTitle)
  }

  async function handleDuplicate() {
    const id = get(currentPlanId)
    if (id) await duplicatePlan(id)
  }

  async function handleDelete() {
    const id = get(currentPlanId)
    if (!id || id === 'default') return
    if (!confirm(`Delete plan "${id}"?`)) return
    await deletePlan(id)
  }

  function exportPlan() {
    const p = get(plan)
    if (!p) return
    const blob = new Blob([JSON.stringify(p, null, 2)], { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `${get(currentPlanId) || 'plan'}.json`
    a.click()
    URL.revokeObjectURL(a.href)
  }

  async function importPlan(file) {
    const text = await file.text()
    const data = JSON.parse(text)
    const id = (file.name || 'import').replace(/\.json$/i, '')
    await createPlan(data.header?.projectTitle || id, id)
    await savePlan(data, get(currentPlanId))
  }
</script>

<div class="plan-toolbar no-print">
  <input
    type="search"
    class="plan-search"
    placeholder="Search plans…"
    value={$planSearch}
    on:input={onSearchInput}
    aria-label="Search plans"
  />
  {#if canWrite()}
    <input type="text" class="new-title" bind:value={newTitle} placeholder="New project title" aria-label="New project title" />
    <button type="button" on:click={handleNew}>New</button>
    <button type="button" on:click={handleDuplicate} disabled={!$currentPlanId}>Duplicate</button>
    <button type="button" on:click={handleDelete} disabled={!$currentPlanId || $currentPlanId === 'default'}>Delete</button>
  {/if}
  <button type="button" on:click={exportPlan} disabled={!$plan}>Export</button>
  <label class="import-btn">
    Import
    <input type="file" accept="application/json" bind:this={importInput} hidden on:change={(e) => e.target.files?.[0] && importPlan(e.target.files[0])} />
  </label>
</div>

<style>
  .plan-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  .plan-search, .new-title {
    padding: 0.3rem 0.5rem;
    font-size: 0.8125rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    min-width: 8rem;
  }
  button, .import-btn {
    padding: 0.3rem 0.6rem;
    font-size: 0.75rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface-elevated);
    cursor: pointer;
  }
  button:hover:not(:disabled), .import-btn:hover { border-color: var(--color-accent); }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .import-btn { display: inline-flex; align-items: center; }
</style>
