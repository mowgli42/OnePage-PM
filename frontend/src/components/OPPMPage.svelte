<script>
  import { onMount } from 'svelte'
  import { plan, planLoading, planSaving, planError, fetchPlan, savePlan, defaultPlan } from '../stores/plan.js'

  let editing = false
  let planData = null

  function normalizePlan(p) {
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

  $: if ($plan != null && planData == null) planData = normalizePlan(JSON.parse(JSON.stringify($plan)))
  $: if ($plan == null && !$planLoading && planData == null) planData = normalizePlan(JSON.parse(JSON.stringify(defaultPlan)))

  onMount(() => fetchPlan())

  async function handleSave() {
    if (!planData) return
    try {
      await savePlan(planData)
      editing = false
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

  const SYMBOLS = [
    { value: '', label: '—' },
    { value: '○', label: '○ Planned' },
    { value: '●', label: '● Done' },
    { value: '△', label: '△ Risk' },
  ]

  const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0)

  const display = planData || {}
  const header = display.header || {}
  const quarters = display.quarters || []
  const objectives = display.objectives || []
  const matrix = display.matrix || []
  const owners = display.owners || []
  const budget = display.budget || { total: 0, spent: 0, categories: [] }
  const risks = display.risks || []
  const kpis = display.kpis || []
  const status = display.status || { level: 'yellow', text: '' }
</script>

<div class="oppm">
  <div class="oppm-actions no-print">
    <button type="button" on:click={() => window.print()}>Print one page</button>
    {#if !editing}
      <button type="button" on:click={() => editing = true}>Edit plan</button>
    {:else}
      <button type="button" on:click={handleSave} disabled={$planSaving}>{$planSaving ? 'Saving…' : 'Save plan'}</button>
      <button type="button" on:click={() => editing = false} disabled={$planSaving}>Cancel</button>
    {/if}
    <span class="hint">Budget & schedule are highlighted for printing.</span>
  </div>

  {#if $planError}
    <p class="plan-error no-print">Could not load or save plan: {$planError}. Start the backend to persist changes.</p>
  {/if}
  {#if $planLoading && !planData}
    <p class="plan-loading no-print">Loading plan…</p>
  {/if}

  {#if editing && planData}
    <div class="edit-panel no-print">
      <h3>Edit project plan</h3>
      <div class="edit-section">
        <h4>Header</h4>
        <label>Project title <input type="text" bind:value={planData.header.projectTitle} /></label>
        <label>Sponsor <input type="text" bind:value={planData.header.sponsor} /></label>
        <label>Project manager <input type="text" bind:value={planData.header.projectManager} /></label>
        <label>Start date <input type="text" bind:value={planData.header.startDate} /></label>
        <label>End date <input type="text" bind:value={planData.header.endDate} /></label>
        <label>Reporting period <input type="text" bind:value={planData.header.reportingPeriod} /></label>
        <label>Version <input type="text" bind:value={planData.header.version} /></label>
        <label>Date updated <input type="text" bind:value={planData.header.dateUpdated} /></label>
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
        <label>Status text <input type="text" bind:value={planData.status.text} class="wide" /></label>
      </div>
      <div class="edit-section">
        <h4>Budget</h4>
        <label>Total <input type="number" bind:value={planData.budget.total} min="0" /></label>
        <label>Spent <input type="number" bind:value={planData.budget.spent} min="0" /></label>
        {#each planData.budget.categories as cat}
          <div class="edit-row">
            <input type="text" bind:value={cat.name} placeholder="Category" />
            <input type="number" bind:value={cat.planned} min="0" placeholder="Planned" />
            <input type="number" bind:value={cat.spent} min="0" placeholder="Spent" />
          </div>
        {/each}
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

  <!-- 1. Header Block -->
  <header class="oppm-header">
    <div class="header-row">
      <span class="field"><strong>Project:</strong> {header.projectTitle}</span>
      <span class="field"><strong>Sponsor:</strong> {header.sponsor}</span>
      <span class="field"><strong>PM:</strong> {header.projectManager}</span>
    </div>
    <div class="header-row">
      <span class="field">{header.startDate} – {header.endDate}</span>
      <span class="field"><strong>Period:</strong> {header.reportingPeriod}</span>
      <span class="field">{header.version} / {header.dateUpdated}</span>
    </div>
  </header>

  <!-- 2–4. Objectives + Timeline + Matrix (schedule – key data) -->
  <div class="oppm-matrix-wrap key-data schedule-block">
    <table class="oppm-matrix">
      <thead>
        <tr>
          <th class="obj-col">Objectives</th>
          {#each quarters as q}
            <th class="quarter">{q}</th>
          {/each}
          <th class="owner-col">Owner</th>
        </tr>
      </thead>
      <tbody>
        {#each objectives as obj, i}
          <tr>
            <td class="obj-cell">
              <span class="obj-id">{obj.id}</span>
              <span class="obj-title">{obj.title}</span>
              <span class="obj-metric">{obj.metric}</span>
            </td>
            {#each matrix[i] as cell}
              <td class="matrix-cell">
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

  <!-- 5. Owners legend -->
  <div class="oppm-owners">
    <strong>Owners:</strong>
    {#each owners as o}
      <span class="owner-entry">{o.initials} = {o.role}</span>
    {/each}
  </div>

  <!-- 6–8. Bottom band: Budget | Risks & KPIs | Status -->
  <div class="oppm-bottom">
    <div class="block budget-block key-data">
      <h4>Budget / Effort</h4>
      <p class="total">Total: ${(budget.total / 1000).toFixed(0)}k | Spent: ${(budget.spent / 1000).toFixed(1)}k ({pct(budget.spent, budget.total)}%)</p>
      <div class="bar">
        <div class="bar-fill" style="width: {pct(budget.spent, budget.total)}%"></div>
      </div>
      <ul>
        {#each budget.categories as c}
          <li>{c.name}: {pct(c.spent, c.planned)}%</li>
        {/each}
      </ul>
    </div>

    <div class="block risks-block">
      <h4>Risks & KPIs</h4>
      <div class="risks">
        {#each risks as r}
          <p><strong>{r.owner}:</strong> {r.text} — {r.mitigation}</p>
        {/each}
      </div>
      <div class="kpis">
        {#each kpis as k}
          <p><span class={k.target ? '' : 'below-target'}>{k.label}: {k.value}</span></p>
        {/each}
      </div>
    </div>

    <div class="block status-block">
      <h4>Status & Legend</h4>
      <p class="status-{status.level}">
        <span class="status-dot {status.level}"></span>
        <strong>{status.level.toUpperCase()}</strong> – {status.text}
      </p>
      <div class="legend">
        <span>○ Planned</span>
        <span>● Done</span>
        <span>△ Risk</span>
      </div>
    </div>
  </div>
</div>

<style>
  .oppm {
    font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
    font-size: 12px;
    max-width: 1100px;
    margin: 0 auto;
    padding: 1rem;
    background: #fff;
    color: #1a1a1a;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    --ixdf-space: 0.5rem;
    --ixdf-key: #e87900;
  }

  .oppm-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }
  .oppm-actions button {
    padding: 0.4rem 0.75rem;
    font-size: 0.875rem;
    background: var(--ixdf-key);
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  .oppm-actions button:hover { filter: brightness(1.05); }
  .oppm-actions .hint { color: #64748b; font-size: 0.8rem; }
  @media print { .no-print { display: none !important; } }

  .plan-error { color: #b91c1c; font-size: 0.9rem; margin: 0 0 0.5rem; }
  .plan-loading { color: #64748b; margin: 0 0 0.5rem; }

  .edit-panel {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .edit-panel h3 { margin: 0 0 0.75rem; font-size: 1rem; }
  .edit-section { margin-bottom: 1rem; }
  .edit-section h4 { margin: 0 0 0.5rem; font-size: 0.85rem; color: #475569; }
  .edit-panel label { display: block; margin: 0.25rem 0; font-size: 0.875rem; }
  .edit-panel input, .edit-panel select { margin-left: 0.5rem; padding: 0.25rem 0.5rem; }
  .edit-panel input.wide { width: 20rem; max-width: 100%; }
  .edit-row { display: flex; gap: 0.5rem; margin: 0.25rem 0; flex-wrap: wrap; align-items: center; }
  .edit-row input { flex: 1; min-width: 80px; }
  .edit-hint { font-size: 0.8rem; color: #64748b; margin: 0 0 0.5rem; }
  .schedule-edit { border-top: 1px solid #e2e8f0; padding-top: 1rem; }
  .btn-sm { width: 2rem; padding: 0.2rem; font-size: 1rem; line-height: 1; cursor: pointer; border: 1px solid #cbd5e1; border-radius: 4px; background: #fff; }
  .btn-sm:hover:not(:disabled) { background: #f1f5f9; }
  .btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-add { margin-top: 0.5rem; padding: 0.35rem 0.75rem; font-size: 0.875rem; background: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 6px; cursor: pointer; }
  .btn-add:hover { background: #cbd5e1; }
  .period-input { max-width: 12rem; }
  .objective-edit { margin-bottom: 0.35rem; }
  .id-input { max-width: 3rem; }
  .title-input { min-width: 10rem; }
  .owner-input { max-width: 4rem; }
  .matrix-edit-wrap { overflow-x: auto; margin-top: 0.5rem; }
  .matrix-edit-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
  .matrix-edit-table th, .matrix-edit-table td { border: 1px solid #e2e8f0; padding: 0.25rem; vertical-align: top; }
  .matrix-edit-table th { background: #f1f5f9; text-align: left; }
  .matrix-edit-table .obj-ref { font-weight: 600; width: 2.5rem; }
  .cell-edit { min-width: 6rem; }
  .cell-edit select { display: block; width: 100%; margin-bottom: 0.2rem; font-size: 0.75rem; }
  .cell-edit .cell-label { width: 100%; font-size: 0.75rem; padding: 0.15rem; }

  .oppm-header {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.5rem 0.75rem;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    margin: -1rem -1rem 1rem -1rem;
    border-radius: 8px 8px 0 0;
  }

  .header-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .header-row .field { white-space: nowrap; }

  .oppm-matrix-wrap {
    overflow-x: auto;
  }

  .oppm-matrix {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }

  .oppm-matrix th, .oppm-matrix td {
    border: 1px solid #e2e8f0;
    padding: 0.4rem 0.5rem;
    vertical-align: top;
  }

  .oppm-matrix th {
    background: #f1f5f9;
    font-weight: 600;
  }

  .obj-col { width: 180px; }
  .owner-col { width: 50px; text-align: center; }
  .quarter { width: 14%; }

  .obj-cell {
    display: flex;
    flex-direction: column;
  }

  .obj-id { font-weight: 600; color: #475569; }
  .obj-title { font-size: 11px; }
  .obj-metric { font-size: 10px; color: #64748b; }

  .matrix-cell {
    text-align: center;
    font-size: 11px;
  }

  .symbol { font-size: 1.2em; }
  .label { display: block; font-size: 10px; color: #64748b; }

  .oppm-owners {
    margin-top: 0.5rem;
    padding: 0.4rem 0;
    font-size: 11px;
    color: #64748b;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .owner-entry { white-space: nowrap; }

  .oppm-bottom {
    display: grid;
    grid-template-columns: 1fr 1.2fr 1fr;
    gap: 1rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #e2e8f0;
  }

  .block h4 {
    margin: 0 0 0.5rem;
    font-size: 11px;
    text-transform: uppercase;
    color: #64748b;
  }

  .block p, .block li { margin: 0.25rem 0; font-size: 11px; }
  .block ul { margin: 0; padding-left: 1rem; }

  .bar {
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    overflow: hidden;
    margin: 0.4rem 0;
  }

  .bar-fill {
    height: 100%;
    background: #3b82f6;
  }

  .below-target { color: #dc2626; }

  .status-yellow .status-dot { background: #eab308; }
  .status-green .status-dot { background: #22c55e; }
  .status-red .status-dot { background: #dc2626; }
  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.3rem;
  }

  .legend { font-size: 10px; color: #94a3b8; margin-top: 0.3rem; }
  .legend span { margin-right: 0.75rem; }

  /* Key data (budget / schedule) – ixdf-style highlight */
  .key-data { border-left: 3px solid var(--ixdf-key); padding-left: var(--ixdf-space); margin-left: calc(-1 * var(--ixdf-space)); }
  .oppm-matrix-wrap.key-data { margin-left: 0; padding-left: 0; border-left: none; border: 2px solid var(--ixdf-key); border-radius: 6px; padding: 0.25rem; }
  .budget-block.key-data { border-left-width: 4px; }

  @media (max-width: 768px) {
    .oppm-bottom { grid-template-columns: 1fr; }
    .oppm-matrix { font-size: 10px; }
  }

  @media print {
    .oppm {
      box-shadow: none;
      border: 1px solid #111;
      max-width: none;
      width: 100%;
      padding: 0.5rem;
      break-inside: avoid;
      page-break-inside: avoid;
    }
    .oppm-header { background: #f5f5f5; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    /* Single page: fit content to one landscape sheet */
    .oppm { font-size: 10px; }
    .oppm-matrix th, .oppm-matrix td { padding: 0.25rem 0.35rem; }
    .obj-col { width: 140px; }
    .block p, .block li { font-size: 10px; }
    /* Highlight budget and schedule for print */
    .key-data {
      border-color: #000 !important;
      background: #faf8f5 !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    .oppm-matrix-wrap.key-data { border: 2px solid #000; background: #f8faf5 !important; }
    .budget-block.key-data { border-left: 4px solid #000; background: #faf8f5 !important; }
  }
</style>
