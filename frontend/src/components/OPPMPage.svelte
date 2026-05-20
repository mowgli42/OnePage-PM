<script>
  import { onMount } from 'svelte'
  import { plan, planLoading, planSaving, planError, fetchPlan, savePlan, fetchPlans, defaultPlan, oppmEditing } from '../stores/plan.js'
  import { canWrite } from '../stores/auth.js'
  import PlanToolbar from './PlanToolbar.svelte'
  import GanttView from './GanttView.svelte'

  let planData = null
  $: editing = $oppmEditing

  function normalizePlan(p) {
    if (!p) return null
    const q = p?.quarters?.length ?? 0
    const objs = p?.objectives ?? []
    let matrix = p?.matrix ?? []
    // Ensure matrix has one row per objective
    while (matrix.length < objs.length) {
      matrix = [...matrix, Array(q).fill(null).map(() => ({ symbol: '', label: '' }))]
    }
    matrix = matrix.slice(0, objs.length)
    // Ensure each row has one cell per period
    matrix = matrix.map((row) => {
      const r = [...(row || [])]
      while (r.length < q) r.push({ symbol: '', label: '' })
      return r.slice(0, q)
    })
    return { ...p, matrix }
  }

  /* Ensure we always have data to show and edit: init from default, reactive will replace with $plan when fetch completes. */
  $: if (planData == null) planData = normalizePlan(JSON.parse(JSON.stringify(defaultPlan)))

  /* Prefer $plan when available so fetch/save response is shown; do not overwrite while user is editing (keeps bind:value working). */
  $: {
    if ($plan != null && !$oppmEditing) {
      planData = normalizePlan(JSON.parse(JSON.stringify($plan)))
    } else if (!$planLoading && planData == null) {
      planData = normalizePlan(JSON.parse(JSON.stringify(defaultPlan)))
    }
  }

  onMount(async () => {
    await fetchPlans()
    await fetchPlan()
  })

  async function handleSave() {
    if (!planData) return
    try {
      // Persist category-derived totals so read view and reports stay correct
      if (planData.budget?.categories?.length) {
        planData.budget.total = budgetCategories.reduce((s, c) => s + (Number(c.planned) || 0), 0)
        planData.budget.spent = budgetCategories.reduce((s, c) => s + (Number(c.spent) || 0), 0)
      }
      await savePlan(planData)
      oppmEditing.set(false)
    } catch (_) { /* planError set in store */ }
  }

  function addObjective() {
    if (!planData) return
    const n = planData.objectives.length
    const owner = planData.owners[0]?.initials || ''
    planData.objectives = [...planData.objectives, { id: `O${n + 1}`, title: '', metric: '', owner }]
    planData.matrix = [...planData.matrix, (planData.quarters || []).map(() => ({ symbol: '', label: '' }))]
  }

  function removeObjective(i) {
    if (!planData || planData.objectives.length <= 1) return
    planData.objectives = planData.objectives.filter((_, idx) => idx !== i)
    planData.matrix = planData.matrix.filter((_, idx) => idx !== i)
  }

  function addQuarter() {
    if (!planData) return
    const quarters = planData.quarters || []
    planData.quarters = [...quarters, 'New period']
    planData.matrix = planData.matrix.map((row) => [...row, { symbol: '', label: '' }])
  }

  function removeQuarter(j) {
    if (!planData || (planData.quarters || []).length <= 1) return
    planData.quarters = planData.quarters.filter((_, idx) => idx !== j)
    planData.matrix = planData.matrix.map((row) => row.filter((_, idx) => idx !== j))
  }

  function addBudgetCategory() {
    if (!planData?.budget?.categories) return
    planData.budget.categories = [...planData.budget.categories, { name: '', planned: 0, spent: 0 }]
  }

  function removeBudgetCategory(i) {
    if (!planData?.budget?.categories || planData.budget.categories.length <= 1) return
    planData.budget.categories = planData.budget.categories.filter((_, idx) => idx !== i)
  }

  function addTask() {
    if (!planData) return
    planData.tasks = [...(planData.tasks || []), {
      id: `T${(planData.tasks?.length || 0) + 1}`,
      title: '',
      startDate: planData.header?.startDate || '',
      endDate: planData.header?.endDate || '',
      dependsOn: [],
      progress: 0,
    }]
  }

  function removeTask(i) {
    if (!planData?.tasks) return
    planData.tasks = planData.tasks.filter((_, idx) => idx !== i)
  }

  const SYMBOLS = [
    { value: '', label: '—' },
    { value: '○', label: '○ Planned' },
    { value: '●', label: '● Done' },
    { value: '△', label: '△ Risk' },
  ]

  const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0)

  /** Index of the current reporting period in quarters (for table column highlight). -1 if none. */
  $: currentPeriodIndex = (() => {
    const qs = planData?.quarters || []
    const rp = planData?.header?.reportingPeriod ?? ''
    if (!rp || !qs.length) return -1
    const i = qs.findIndex((q) => String(q).toLowerCase().includes(rp.toLowerCase()) || rp.toLowerCase().includes(String(q).toLowerCase()))
    return i >= 0 ? i : (qs.length > 0 ? 0 : -1)
  })()

  const display = planData || {}
  const header = display.header || {}
  const quarters = display.quarters || []
  const objectives = display.objectives || []
  const matrix = display.matrix || []
  const owners = display.owners || []
  const budget = display.budget || { total: 0, spent: 0, categories: [] }

  /** Totals derived from category line items (allocated budget vs tracked spend). */
  $: budgetCategories = planData?.budget?.categories ?? []
  $: sumPlanned = budgetCategories.reduce((s, c) => s + (Number(c.planned) || 0), 0)
  $: sumSpent = budgetCategories.reduce((s, c) => s + (Number(c.spent) || 0), 0)
  const risks = display.risks || []
  const kpis = display.kpis || []
  const status = display.status || { level: 'yellow', text: '' }
</script>

<div class="oppm">
  <PlanToolbar />
  {#if $planError}
    <p class="plan-error no-print" role="alert">Could not load or save plan: {$planError}. Start the backend to persist changes.</p>
  {/if}
  {#if $planLoading && !planData}
    <p class="plan-loading no-print">Loading plan…</p>
  {/if}

  {#if editing && planData}
    <div class="edit-panel no-print" role="form" aria-label="Edit project plan">
      <div class="edit-panel-head">
        <h3>Edit project plan</h3>
        <div class="edit-panel-actions">
          <button type="button" class="btn-icon btn-save" on:click={handleSave} disabled={$planSaving} aria-label={$planSaving ? 'Saving…' : 'Save plan'} title={$planSaving ? 'Saving…' : 'Save plan'}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          </button>
          <button type="button" class="btn-secondary" on:click={() => oppmEditing.set(false)} disabled={$planSaving}>Cancel</button>
        </div>
      </div>
      <div class="edit-section edit-section-header">
        <h4>Header</h4>
        <div class="edit-header-grid">
          <label>Project title <input type="text" bind:value={planData.header.projectTitle} /></label>
          <label>Sponsor <input type="text" bind:value={planData.header.sponsor} /></label>
          <label>Project manager <input type="text" bind:value={planData.header.projectManager} /></label>
          <label>Start date <input type="text" bind:value={planData.header.startDate} /></label>
          <label>End date <input type="text" bind:value={planData.header.endDate} /></label>
          <label>Reporting period <input type="text" bind:value={planData.header.reportingPeriod} /></label>
          <label>Version <input type="text" bind:value={planData.header.version} /></label>
          <label>Date updated <input type="text" bind:value={planData.header.dateUpdated} /></label>
        </div>
      </div>
      <div class="edit-section">
        <h4>Status</h4>
        <label>Level
          <select bind:value={planData.status.level}>
            <option value="green">Green</option>
            <option value="yellow">Yellow</option>
            <option value="red">Red</option>
          </select>
        </label>
        <label class="label-block">Status summary <textarea bind:value={planData.status.text} class="status-summary" rows="4" placeholder="Paragraph or summary of current status…"></textarea></label>
      </div>
      <div class="edit-section">
        <h4>Budget</h4>
        <p class="edit-hint">Add categories with planned budget and spent. Totals are calculated from the rows so you can see that all budget is allocated and all spend is tracked.</p>
        <div class="budget-totals budget-totals-computed" role="status" aria-live="polite">
          <span class="budget-sum">Total from categories — Budget (planned): <strong>{sumPlanned.toLocaleString()}</strong></span>
          <span class="budget-sum">Spent: <strong>{sumSpent.toLocaleString()}</strong></span>
        </div>
        <div class="budget-table-wrap">
          <div class="budget-row budget-row-head">
            <span class="budget-col-name">Category</span>
            <span class="budget-col-num">Budget (planned)</span>
            <span class="budget-col-num">Spent</span>
            <span class="budget-col-action"></span>
          </div>
          {#each planData.budget.categories as cat, i}
            <div class="edit-row budget-row">
              <input type="text" bind:value={cat.name} placeholder="Category name" class="budget-col-name" />
              <input type="number" bind:value={cat.planned} min="0" placeholder="0" class="budget-col-num" />
              <input type="number" bind:value={cat.spent} min="0" placeholder="0" class="budget-col-num" />
              <button type="button" class="btn-icon btn-delete" on:click={() => removeBudgetCategory(i)} disabled={(planData.budget.categories || []).length <= 1} title="Remove category" aria-label="Remove category">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6M8 5V4a1 1 0 011-1h4a1 1 0 011 1v1m-6 2h12"/></svg>
              </button>
            </div>
          {/each}
        </div>
        <button type="button" class="btn-add" on:click={addBudgetCategory}>+ Add budget line</button>
      </div>

      <div class="edit-section schedule-edit">
        <h4>Schedule – Time periods</h4>
        <p class="edit-hint">Columns in the timeline matrix (e.g. Q1 2026, Q2 2026).</p>
        {#each planData.quarters || [] as q, j}
          <div class="edit-row">
            <input type="text" bind:value={planData.quarters[j]} placeholder="Period label" class="period-input" />
            <button type="button" class="btn-sm" on:click={() => removeQuarter(j)} disabled={(planData.quarters || []).length <= 1} title="Remove period">−</button>
          </div>
        {/each}
        <button type="button" class="btn-add" on:click={addQuarter}>+ Add period</button>
      </div>

      <div class="edit-section schedule-edit">
        <h4>Schedule – Objectives</h4>
        <p class="edit-hint">Rows in the matrix (id, title, success metric, owner).</p>
        {#each planData.objectives || [] as obj, i}
          <div class="objective-edit">
            <div class="edit-row">
              <input type="text" bind:value={obj.id} placeholder="O1" class="id-input" />
              <input type="text" bind:value={obj.title} placeholder="Objective title" class="title-input" />
              <input type="text" bind:value={obj.metric} placeholder="Success metric" />
              <input type="text" bind:value={obj.owner} placeholder="Owner" class="owner-input" />
              <button type="button" class="btn-sm" on:click={() => removeObjective(i)} disabled={(planData.objectives || []).length <= 1} title="Remove objective">−</button>
            </div>
          </div>
        {/each}
        <button type="button" class="btn-add" on:click={addObjective}>+ Add objective</button>
      </div>

      <div class="edit-section schedule-edit">
        <h4>Timeline tasks (Gantt)</h4>
        {#each planData.tasks || [] as task, ti}
          <div class="edit-row">
            <input type="text" bind:value={task.id} placeholder="T1" class="id-input" />
            <input type="text" bind:value={task.title} placeholder="Title" class="title-input" />
            <input type="text" bind:value={task.startDate} placeholder="Start" />
            <input type="text" bind:value={task.endDate} placeholder="End" />
            <button type="button" class="btn-sm" on:click={() => removeTask(ti)}>−</button>
          </div>
        {/each}
        <button type="button" class="btn-add" on:click={addTask}>+ Add task</button>
      </div>

      <div class="edit-section schedule-edit">
        <h4>Schedule – Matrix (milestones per objective × period)</h4>
        <p class="edit-hint">○ Planned, ● Done, △ Risk. Set symbol and short label per cell.</p>
        <div class="matrix-edit-wrap">
          <table class="matrix-edit-table">
            <thead>
              <tr>
                <th>Objective</th>
                {#each planData.quarters || [] as q}
                  <th>{q}</th>
                {/each}
              </tr>
            </thead>
            <tbody>
              {#each (planData.objectives || []) as obj, i}
                <tr>
                  <td class="obj-ref">{obj.id}</td>
                  {#each (planData.matrix[i] || []) as cell, j}
                    <td class="cell-edit">
                      <select bind:value={cell.symbol} title="Symbol">
                        {#each SYMBOLS as s}
                          <option value={s.value}>{s.label}</option>
                        {/each}
                      </select>
                      <input type="text" bind:value={cell.label} placeholder="Label" class="cell-label" />
                    </td>
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  {/if}

  {#if planData && !editing}
  <!-- Read-only preview (hidden while editing) -->
  <!-- Top row: project name (bold, prominent) aligned with status -->
  <div class="oppm-top-row">
    <h2 class="oppm-project-title">{planData.header?.projectTitle ?? 'Project'}</h2>
    <div class="status-badge status-{planData.status?.level ?? 'yellow'}">
      <span class="status-dot-lg {planData.status?.level ?? 'yellow'}"></span>
      <span class="status-label">{(planData.status?.level ?? 'yellow').toUpperCase()}</span>
      <span class="status-text">{planData.status?.text ?? ''}</span>
    </div>
  </div>

  <!-- Header meta: sponsor, PM, dates, version (no period label here – current period highlighted in table) -->
  <header class="oppm-header">
    <div class="header-row">
      <span class="field"><strong>Sponsor:</strong> {planData.header?.sponsor ?? ''}</span>
      <span class="field"><strong>PM:</strong> {planData.header?.projectManager ?? ''}</span>
      <span class="field">{planData.header?.startDate ?? ''} – {planData.header?.endDate ?? ''}</span>
      <span class="field">{planData.header?.version ?? ''} / {planData.header?.dateUpdated ?? ''}</span>
    </div>
  </header>

  <GanttView tasks={planData.tasks || []} />

  <!-- 2–4. Objectives + Timeline + Matrix (schedule – key data) -->
  <div class="oppm-matrix-wrap key-data schedule-block">
    <table class="oppm-matrix">
      <thead>
        <tr>
          <th class="obj-col">Objectives</th>
          {#each (planData.quarters || []) as q, j}
            <th class="quarter" class:quarter-current={j === currentPeriodIndex}>{q}</th>
          {/each}
          <th class="owner-col">Owner</th>
        </tr>
      </thead>
      <tbody>
        {#each planData.objectives || [] as obj, i}
          <tr>
            <td class="obj-cell">
              <span class="obj-id">{obj.id}</span>
              <span class="obj-title">{obj.title}</span>
              <span class="obj-metric">{obj.metric}</span>
            </td>
            {#each (planData.matrix || [])[i] || [] as cell, j}
              <td class="matrix-cell" class:quarter-current={j === currentPeriodIndex}>
                {#if cell.symbol}
                  <span class="symbol" data-symbol={cell.symbol}>{cell.symbol}</span>
                  {#if cell.label}<span class="label">{cell.label}</span>{/if}
                {/if}
              </td>
            {/each}
            <td class="owner-cell">{obj.owner}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- 5. Owners row with legend on far right -->
  <div class="oppm-owners-row">
    <div class="oppm-owners">
      <strong>Owners:</strong>
      {#each planData.owners || [] as o}
        <span class="owner-entry">{o.initials} = {o.role}</span>
      {/each}
    </div>
    <div class="legend-inline">
      <span class="legend-planned">○ Planned</span>
      <span class="legend-done">● Done</span>
      <span class="legend-risk">△ Risk</span>
    </div>
  </div>

  <!-- 6–8. Bottom band: Budget | Risks | KPIs -->
  <div class="oppm-bottom">
    <div class="block budget-block key-data">
      <h4>Budget / Effort</h4>
      <p class="total">Total: ${((planData.budget?.total ?? 0) / 1000).toFixed(0)}k | Spent: ${((planData.budget?.spent ?? 0) / 1000).toFixed(1)}k ({pct(planData.budget?.spent ?? 0, planData.budget?.total ?? 1)}%)</p>
      <div class="bar">
        <div class="bar-fill" style="width: {pct(planData.budget?.spent ?? 0, planData.budget?.total ?? 1)}%"></div>
      </div>
      <ul>
        {#each planData.budget?.categories || [] as c}
          <li>{c.name}: {pct(c.spent, c.planned)}%</li>
        {/each}
      </ul>
    </div>

    <div class="block risks-block">
      <h4>Risks</h4>
      <div class="risks">
        {#each planData.risks || [] as r}
          <p><strong>{r.owner}:</strong> {r.text} — {r.mitigation}</p>
        {/each}
      </div>
    </div>

    <div class="block kpis-block">
      <h4>KPIs</h4>
      <div class="kpis">
        {#each planData.kpis || [] as k}
          <p><span class={k.target ? '' : 'below-target'}>{k.label}: {k.value}</span></p>
        {/each}
      </div>
    </div>
  </div>
  {/if}
</div>

<style>
  .oppm {
    font-family: var(--font-body);
    font-size: 11px;
    max-width: 1100px;
    margin: 0 auto;
    padding: 0.75rem 1rem;
    background: var(--color-surface-elevated);
    color: var(--color-base);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    --key-space: 0.4rem;
    --key-accent: var(--color-secondary);
  }

  /* Top row: project name (bold, bigger) aligned with status */
  .oppm-top-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);
  }
  .oppm-project-title {
    margin: 0;
    font-family: var(--font-display);
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--color-base);
    letter-spacing: -0.02em;
    line-height: 1.2;
  }
  .status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.75rem;
    border-radius: var(--radius-md);
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    font-size: 0.8125rem;
  }
  .status-dot-lg {
    display: inline-block;
    width: 1.25rem;
    height: 1.25rem;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .status-dot-lg.green { background: var(--color-done); }
  .status-dot-lg.yellow { background: var(--color-warn); }
  .status-dot-lg.red { background: var(--color-risk); }
  .status-badge { font-size: 0.9375rem; }
  .status-label { font-weight: 600; color: var(--color-base); }
  .status-text { color: var(--color-base-muted); max-width: 20rem; }
  @media print { .no-print { display: none !important; } }

  .plan-error {
    padding: 0.5rem 0.75rem;
    background: var(--color-error-bg);
    border: 1px solid var(--color-error-border);
    border-radius: var(--radius-md);
    color: var(--color-error-text);
    font-size: 0.875rem;
    margin: 0 0 0.5rem;
  }
  .plan-loading { color: var(--color-base-muted); font-size: 0.875rem; margin: 0 0 0.4rem; }

  .edit-panel {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 0.875rem 1rem;
    margin-bottom: 0.75rem;
  }
  .edit-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }
  .edit-panel-head h3 {
    margin: 0;
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-base);
  }
  .edit-panel-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .edit-panel-actions .btn-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
    border: none;
    border-radius: var(--radius-md);
    cursor: pointer;
    color: white;
    background: var(--color-accent);
  }
  .edit-panel-actions .btn-icon:hover:not(:disabled) { background: var(--color-accent-hover); }
  .edit-panel-actions .btn-icon:disabled { opacity: 0.6; cursor: not-allowed; }
  .edit-panel-actions .btn-icon:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 2px; }
  .edit-panel-actions .btn-secondary {
    padding: 0.4rem 0.75rem;
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--color-base-muted);
    background: var(--color-surface-elevated);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    cursor: pointer;
  }
  .edit-panel-actions .btn-secondary:hover:not(:disabled) { background: var(--color-surface); }
  .edit-section { margin-bottom: 1.25rem; }
  .edit-section h4 {
    margin: 0 0 0.5rem;
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-base-muted);
  }
  .edit-header-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem 1.25rem;
  }
  .edit-header-grid label {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    font-size: 0.875rem;
  }
  .edit-header-grid input { margin-left: 0; }
  @media (max-width: 640px) {
    .edit-header-grid { grid-template-columns: 1fr; }
  }
  .edit-panel label { display: block; margin: 0.35rem 0; font-size: 0.875rem; }
  .edit-panel label.label-block { display: block; }
  .edit-panel input, .edit-panel select, .edit-panel textarea {
    margin-left: 0.5rem;
    padding: 0.35rem 0.5rem;
    font-family: var(--font-body);
    font-size: 0.9375rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface-elevated);
  }
  .edit-panel .status-summary {
    width: 100%;
    min-height: 6rem;
    resize: vertical;
    margin-top: 0.25rem;
    margin-left: 0;
  }
  .edit-panel input:focus, .edit-panel select:focus, .edit-panel textarea:focus {
    outline: none;
    border-color: var(--color-accent);
    box-shadow: 0 0 0 2px var(--color-accent-muted);
  }
  .budget-totals {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }
  .budget-totals-computed {
    flex-wrap: wrap;
    gap: 0.5rem 1.5rem;
    font-size: 0.9375rem;
  }
  .budget-sum strong { color: var(--color-base); }
  .budget-num { width: 8rem; }
  .btn-icon.btn-delete {
    width: 2.25rem;
    height: 2.25rem;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    background: var(--color-surface-elevated);
    color: var(--color-base-muted);
    transition: background var(--transition), color var(--transition);
  }
  .btn-icon.btn-delete:hover:not(:disabled) {
    background: var(--color-danger-muted, #fef2f2);
    color: var(--color-danger, #b91c1c);
  }
  .btn-icon.btn-delete:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-icon.btn-delete:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 1px; }
  .budget-table-wrap { margin-bottom: 0.5rem; }
  .budget-row-head {
    display: grid;
    grid-template-columns: 1fr 6rem 6rem 2.5rem;
    gap: 0.5rem;
    align-items: center;
    padding: 0.35rem 0;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-base-muted);
    border-bottom: 1px solid var(--color-border);
  }
  .budget-row.edit-row {
    display: grid;
    grid-template-columns: 1fr 6rem 6rem 2.5rem;
    gap: 0.5rem;
    align-items: center;
    margin: 0.25rem 0;
  }
  .budget-row .budget-col-name { min-width: 0; }
  .budget-row .budget-col-num { width: 6rem; min-width: 4rem; }
  .edit-row { display: flex; gap: 0.5rem; margin: 0.35rem 0; flex-wrap: wrap; align-items: center; }
  .edit-row input { flex: 1; min-width: 80px; }
  .edit-hint { font-size: 0.8125rem; color: var(--color-base-muted); margin: 0 0 0.5rem; }
  .schedule-edit { border-top: 1px solid var(--color-border); padding-top: 1rem; }
  .btn-sm {
    width: 2rem; padding: 0.2rem; font-size: 1rem; line-height: 1;
    cursor: pointer; border: 1px solid var(--color-border); border-radius: var(--radius-sm);
    background: var(--color-surface-elevated);
    transition: background var(--transition);
  }
  .btn-sm:hover:not(:disabled) { background: var(--color-surface); }
  .btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-sm:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 1px; }
  .btn-add {
    margin-top: 0.5rem;
    padding: 0.4rem 0.875rem;
    font-size: 0.875rem;
    font-weight: 500;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: background var(--transition);
  }
  .btn-add:hover { background: var(--color-border); }
  .period-input { max-width: 12rem; }
  .objective-edit { margin-bottom: 0.35rem; }
  .id-input { max-width: 3rem; }
  .title-input { min-width: 10rem; }
  .owner-input { max-width: 4rem; }
  .matrix-edit-wrap { overflow-x: auto; margin-top: 0.5rem; }
  .matrix-edit-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  .matrix-edit-table th, .matrix-edit-table td { border: 1px solid var(--color-border-strong); padding: 0.3rem; vertical-align: top; }
  .matrix-edit-table th { background: var(--color-surface); font-weight: 600; color: var(--color-base); border-bottom-width: 2px; }
  .matrix-edit-table .obj-ref { font-weight: 600; width: 2.5rem; }
  .cell-edit { min-width: 6rem; }
  .cell-edit select { display: block; width: 100%; margin-bottom: 0.2rem; font-size: 0.75rem; }
  .cell-edit .cell-label { width: 100%; font-size: 0.75rem; padding: 0.2rem; }

  .oppm-header {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.5rem 0.75rem;
    background: var(--color-surface);
    border-bottom: 1px solid var(--color-border);
    margin: -0.75rem -1rem 0.75rem -1rem;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  }

  .header-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }
  .header-row .field { white-space: nowrap; font-size: 0.8125rem; }

  .oppm-matrix-wrap { overflow-x: auto; }

  .oppm-matrix {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }
  .oppm-matrix th, .oppm-matrix td {
    border: 1px solid var(--color-border-strong);
    padding: 0.45rem 0.5rem;
    vertical-align: top;
  }
  .oppm-matrix thead th {
    border-bottom: 2px solid var(--color-base-muted);
  }
  .oppm-matrix th {
    background: var(--color-surface);
    font-family: var(--font-body);
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: var(--color-base-muted);
  }

  .obj-col { width: 180px; border-right: 2px solid var(--color-base-muted); }
  .owner-col { width: 50px; text-align: center; border-left: 2px solid var(--color-base-muted); }
  .quarter { width: 14%; }
  /* Current reporting period column highlight */
  .oppm-matrix th.quarter-current,
  .oppm-matrix td.quarter-current {
    background: var(--color-secondary-muted);
    border-left: 2px solid var(--color-secondary);
    border-right: 2px solid var(--color-secondary);
  }
  .oppm-matrix th.quarter-current { font-weight: 700; color: var(--color-base); }

  .obj-cell { display: flex; flex-direction: column; }
  .obj-id { font-weight: 600; color: var(--color-base); font-size: 0.75rem; }
  .obj-title { font-size: 11px; }
  .obj-metric { font-size: 10px; color: var(--color-base-muted); }

  .matrix-cell { text-align: center; font-size: 12px; }
  .matrix-cell .symbol {
    font-size: 1.5em;
    font-weight: 700;
    line-height: 1.2;
  }
  .matrix-cell .symbol[data-symbol="●"] { color: var(--color-done); }
  .matrix-cell .symbol[data-symbol="○"] { color: var(--color-planned); }
  .matrix-cell .symbol[data-symbol="△"] { color: var(--color-risk); }
  .label { display: block; font-size: 10px; color: var(--color-base-muted); margin-top: 0.15rem; }

  .oppm-owners-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.5rem;
    padding: 0.4rem 0;
  }
  .oppm-owners {
    font-size: 11px;
    color: var(--color-base-muted);
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: center;
  }
  .owner-entry { white-space: nowrap; }
  .legend-inline {
    font-size: 0.8125rem;
    display: flex;
    gap: 1rem;
    align-items: center;
  }
  .legend-inline span { white-space: nowrap; }
  .legend-inline .legend-done { color: var(--color-done); font-weight: 600; }
  .legend-inline .legend-planned { color: var(--color-planned); }
  .legend-inline .legend-risk { color: var(--color-risk); font-weight: 600; }

  .oppm-bottom {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.75rem;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--color-border);
  }

  .block h4 {
    margin: 0 0 0.5rem;
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-base-muted);
  }
  .block p, .block li { margin: 0.3rem 0; font-size: 11px; }
  .block ul { margin: 0; padding-left: 1rem; }

  .bar {
    height: 6px;
    background: var(--color-border);
    border-radius: 3px;
    overflow: hidden;
    margin: 0.4rem 0;
  }
  .bar-fill { height: 100%; background: var(--color-secondary); border-radius: 3px; }

  .below-target { color: var(--color-error-text); }

  .status-yellow .status-dot { background: var(--color-warn); }
  .status-green .status-dot { background: var(--color-done); }
  .status-red .status-dot { background: var(--color-risk); }
  .status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 0.35rem;
  }


  /* Key data (budget / schedule) – accent highlight */
  .key-data {
    border-left: 3px solid var(--key-accent);
    padding-left: var(--key-space);
    margin-left: calc(-1 * var(--key-space));
  }
  .oppm-matrix-wrap.key-data {
    margin-left: 0; padding-left: 0; border-left: none;
    border: 2px solid var(--key-accent);
    border-radius: var(--radius-md);
    padding: 0.35rem;
  }
  .budget-block.key-data { border-left-width: 4px; }

  @media (max-width: 768px) {
    .oppm-bottom { grid-template-columns: 1fr; }
    .oppm-matrix { font-size: 10px; }
  }

  @media print {
    .oppm {
      box-shadow: none;
      border: 1px solid #1e293b;
      max-width: none;
      width: 100%;
      padding: 0.5rem;
      break-inside: avoid;
      page-break-inside: avoid;
    }
    .oppm-header { background: #f5f5f4; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    /* Single page: fit content to one landscape sheet */
    .oppm { font-size: 10px; }
    .oppm-matrix th, .oppm-matrix td { padding: 0.25rem 0.35rem; }
    .obj-col { width: 140px; }
    .block p, .block li { font-size: 10px; }
    /* Bottom band: three columns (Budget | Risks | KPIs) */
    .oppm-bottom {
      grid-template-columns: 1fr 1fr 1fr;
      gap: 0.5rem;
      margin-top: 0.5rem;
      padding-top: 0.5rem;
    }
    .oppm-bottom .block h4 { margin: 0 0 0.25rem; font-size: 10px; }
    .oppm-bottom .block p, .oppm-bottom .block li { margin: 0.15rem 0; font-size: 9px; }
    .oppm-bottom .risks p, .oppm-bottom .kpis p { margin: 0.15rem 0; font-size: 9px; }
    .oppm-bottom .bar { margin: 0.25rem 0; height: 4px; }
    .legend-inline { font-size: 10px; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .matrix-cell .symbol { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    /* Highlight budget and schedule for print */
    .key-data {
      border-color: #000 !important;
      background: #faf8f5 !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .oppm-matrix-wrap.key-data { border: 2px solid #000; background: #f8faf5 !important; }
    .budget-block.key-data { border-left: 4px solid #000; background: #faf8f5 !important; }
    .oppm-matrix th.quarter-current,
    .oppm-matrix td.quarter-current {
      background: #e0f2fe !important;
      border-left: 2px solid #0d9488 !important;
      border-right: 2px solid #0d9488 !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
  }
</style>
