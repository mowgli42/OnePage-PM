<script>
  // Mock OPPM data - Regional Data Collection Pilot
  const header = {
    projectTitle: 'Regional Data Collection Pilot',
    sponsor: 'NASS Field Operations',
    projectManager: 'Jane Smith',
    startDate: 'Jan 1, 2026',
    endDate: 'Dec 31, 2026',
    reportingPeriod: 'FY Q2 2026',
    version: 'v1.0',
    dateUpdated: 'Feb 19, 2026'
  }

  const quarters = ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026']

  const objectives = [
    { id: 'O1', title: 'Launch pilot in 3 regions', metric: '3/3 regions operational', owner: 'MS' },
    { id: 'O2', title: 'Complete baseline report', metric: 'Report approved', owner: 'JP' },
    { id: 'O3', title: 'Establish QA process (95% pass)', metric: '95% pass rate', owner: 'RK' },
    { id: 'O4', title: 'Train 20 field staff', metric: '20 certified', owner: 'MS' },
    { id: 'O5', title: 'Integrate data into national system', metric: 'API live', owner: 'TL' },
    { id: 'O6', title: 'Publish lessons learned', metric: 'Document released', owner: 'JS' }
  ]

  // Matrix: [objectiveIndex][quarterIndex] = { symbol: '○'|'●'|'△', label: string }
  const matrix = [
    [
      { symbol: '○', label: 'Kickoff' },
      { symbol: '●', label: 'Pilot start' },
      { symbol: '●', label: '3 regions' },
      { symbol: '○', label: 'Handoff' }
    ],
    [
      { symbol: '○', label: 'Scoping' },
      { symbol: '○', label: 'Analysis' },
      { symbol: '●', label: 'Draft' },
      { symbol: '●', label: 'Approved' }
    ],
    [
      { symbol: '△', label: 'Design QA' },
      { symbol: '○', label: 'Build' },
      { symbol: '○', label: 'Test' },
      { symbol: '●', label: '95% pass' }
    ],
    [
      { symbol: '○', label: 'Curriculum' },
      { symbol: '●', label: 'Week 1–2' },
      { symbol: '●', label: 'Week 3–4' },
      { symbol: '○', label: 'Certify' }
    ],
    [
      { symbol: '○', label: 'Specs' },
      { symbol: '○', label: 'Dev' },
      { symbol: '△', label: 'UAT' },
      { symbol: '●', label: 'Live' }
    ],
    [
      { symbol: '', label: '' },
      { symbol: '', label: '' },
      { symbol: '○', label: 'Draft' },
      { symbol: '●', label: 'Release' }
    ]
  ]

  const owners = [
    { initials: 'JS', role: 'Project Manager' },
    { initials: 'JP', role: 'Lead Analyst' },
    { initials: 'MS', role: 'Field Coordinator' },
    { initials: 'RK', role: 'QA Lead' },
    { initials: 'TL', role: 'Systems Integrator' }
  ]

  const budget = {
    total: 170000,
    spent: 38300,
    categories: [
      { name: 'Personnel', planned: 120000, spent: 35000 },
      { name: 'Travel', planned: 15000, spent: 2100 },
      { name: 'Contracts', planned: 25000, spent: 0 },
      { name: 'Other', planned: 10000, spent: 1200 }
    ]
  }

  const risks = [
    { text: 'Region 3 staffing gap', owner: 'MS', mitigation: 'Backup contractor identified' },
    { text: 'Data integration delay', owner: 'TL', mitigation: 'Early API testing in Q2' },
    { text: 'Budget overrun risk', owner: 'JS', mitigation: '10% contingency held' }
  ]

  const kpis = [
    { label: 'Surveys completed', value: '250 / 400', target: true },
    { label: 'Data quality pass rate', value: '92%', target: false },
    { label: 'Staff trained', value: '18 / 20', target: true },
    { label: 'Deliverables on time', value: '4 / 5', target: true }
  ]

  const status = {
    level: 'yellow',
    text: 'Region 3 data collection delayed 2 weeks; mitigation in progress.'
  }

  const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0)
</script>

<div class="oppm">
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

  <!-- 2–4. Objectives + Timeline + Matrix -->
  <div class="oppm-matrix-wrap">
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
    <div class="block budget-block">
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
    font-family: system-ui, -apple-system, sans-serif;
    font-size: 12px;
    max-width: 1100px;
    margin: 0 auto;
    padding: 1rem;
    background: #fff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }

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

  @media (max-width: 768px) {
    .oppm-bottom { grid-template-columns: 1fr; }
    .oppm-matrix { font-size: 10px; }
  }

  @media print {
    .oppm { box-shadow: none; border: 1px solid #ccc; }
    .oppm-header { background: #f5f5f5; }
  }
</style>
