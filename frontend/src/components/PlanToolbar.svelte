<script>
  import { onMount } from 'svelte'
  import {
    currentPlanId,
    planSearch,
    fetchPlans,
    createPlan,
    deletePlan,
    duplicatePlan,
    plan,
    savePlan,
    fetchTemplates,
    createPlanFromTemplate,
    exportIcalUrl,
    exportPrintUrl,
  } from '../stores/plan.js'
  import { canWrite } from '../stores/auth.js'
  import { apiFetch } from '../lib/api.js'
  import { get } from 'svelte/store'

  let newTitle = 'New Project'
  let templates = []
  let selectedTemplate = ''
  let attachments = []
  let attachInput

  onMount(async () => {
    templates = await fetchTemplates()
    if ($currentPlanId) loadAttachments()
  })

  $: if ($currentPlanId) loadAttachments()

  async function loadAttachments() {
    const id = get(currentPlanId)
    if (!id) return
    try {
      const res = await apiFetch(`/attachments?plan_id=${encodeURIComponent(id)}`)
      attachments = res.ok ? await res.json() : []
    } catch {
      attachments = []
    }
  }

  async function onSearchInput(e) {
    planSearch.set(e.target.value)
    await fetchPlans(e.target.value)
  }

  async function handleNew() {
    await createPlan(newTitle)
  }

  async function handleTemplate() {
    if (!selectedTemplate) return
    await createPlanFromTemplate(selectedTemplate)
    selectedTemplate = ''
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

  async function uploadAttachment(file) {
    const id = get(currentPlanId)
    if (!id || !file) return
    const form = new FormData()
    form.append('file', file)
    const res = await apiFetch(`/attachments?plan_id=${encodeURIComponent(id)}`, {
      method: 'POST',
      body: form,
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    await loadAttachments()
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
  {#if templates.length}
    <select bind:value={selectedTemplate} aria-label="Template" class="tpl-select">
      <option value="">From template…</option>
      {#each templates as t}
        <option value={t.id}>{t.title}</option>
      {/each}
    </select>
    <button type="button" on:click={handleTemplate} disabled={!selectedTemplate}>Use template</button>
  {/if}
  {#if canWrite()}
    <input type="text" class="new-title" bind:value={newTitle} placeholder="New project title" aria-label="New project title" />
    <button type="button" on:click={handleNew}>New</button>
    <button type="button" on:click={handleDuplicate} disabled={!$currentPlanId}>Duplicate</button>
    <button type="button" on:click={handleDelete} disabled={!$currentPlanId || $currentPlanId === 'default'}>Delete</button>
  {/if}
  <button type="button" on:click={exportPlan} disabled={!$plan}>Export JSON</button>
  <a class="btn-link" href={exportIcalUrl()} download target="_blank" rel="noopener">iCal</a>
  <a class="btn-link" href={exportPrintUrl()} target="_blank" rel="noopener">Print/PDF</a>
  <label class="import-btn">
    Import JSON
    <input type="file" accept="application/json" hidden on:change={(e) => e.target.files?.[0] && importPlan(e.target.files[0])} />
  </label>
  {#if canWrite() && $currentPlanId}
    <label class="import-btn">
      Attach file
      <input type="file" bind:this={attachInput} hidden on:change={(e) => e.target.files?.[0] && uploadAttachment(e.target.files[0])} />
    </label>
  {/if}
</div>
{#if attachments.length}
  <ul class="attach-list no-print">
    {#each attachments as a (a.id)}
      <li>
        <a href={`/_/backend/attachments/${a.id}`} target="_blank" rel="noopener">{a.filename}</a>
        <span class="meta">({Math.round(a.size / 1024)} KB)</span>
      </li>
    {/each}
  </ul>
{/if}

<style>
  .plan-toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    align-items: center;
    margin-bottom: 0.5rem;
  }
  .plan-search, .new-title, .tpl-select {
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
  .btn-link {
    font-size: 0.75rem;
    padding: 0.3rem 0.5rem;
    color: var(--color-accent);
    text-decoration: none;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface-elevated);
  }
  button:hover:not(:disabled), .import-btn:hover, .btn-link:hover { border-color: var(--color-accent); }
  button:disabled { opacity: 0.5; cursor: not-allowed; }
  .import-btn { display: inline-flex; align-items: center; }
  .attach-list {
    margin: 0 0 0.5rem;
    padding: 0;
    list-style: none;
    font-size: 0.75rem;
  }
  .attach-list .meta { color: var(--color-base-muted); }
</style>
