<script>
  export let tasks = []
  export let warnings = []

  const parseDate = (s) => {
    if (!s) return null
    const d = new Date(s)
    return Number.isNaN(d.getTime()) ? null : d
  }

  $: dated = (tasks || []).map((t) => ({
    ...t,
    start: parseDate(t.startDate),
    end: parseDate(t.endDate) || parseDate(t.startDate),
  })).filter((t) => t.start && t.end)

  $: minStart = dated.length ? Math.min(...dated.map((t) => t.start.getTime())) : Date.now()
  $: maxEnd = dated.length ? Math.max(...dated.map((t) => t.end.getTime())) : Date.now() + 86400000
  $: span = Math.max(maxEnd - minStart, 86400000)

  function leftPct(t) {
    return ((t.start.getTime() - minStart) / span) * 100
  }
  function widthPct(t) {
    return Math.max(2, ((t.end.getTime() - t.start.getTime()) / span) * 100)
  }
</script>

<div class="gantt no-print">
  <h4>Timeline</h4>
  {#if warnings?.length}
    <ul class="gantt-warnings" role="status">
      {#each warnings as w}
        <li>{w}</li>
      {/each}
    </ul>
  {/if}
  {#if !dated.length}
    <p class="gantt-empty">Add tasks with start/end dates in edit mode to see the timeline.</p>
  {:else}
    <div class="gantt-chart" role="img" aria-label="Gantt timeline">
      {#each dated as task (task.id)}
        <div class="gantt-row">
          <span class="gantt-label">{task.title || task.id}</span>
          <div class="gantt-track">
            <div
              class="gantt-bar"
              style="left: {leftPct(task)}%; width: {widthPct(task)}%;"
              title="{task.startDate} – {task.endDate} ({task.progress || 0}%)"
            />
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .gantt { margin: 0.75rem 0; }
  .gantt h4 { margin: 0 0 0.5rem; font-size: 0.9375rem; }
  .gantt-empty { font-size: 0.8125rem; color: var(--color-base-muted); margin: 0; }
  .gantt-warnings { margin: 0 0 0.5rem; padding-left: 1.25rem; font-size: 0.75rem; color: var(--color-warn); }
  .gantt-chart { display: flex; flex-direction: column; gap: 0.35rem; }
  .gantt-row { display: grid; grid-template-columns: 10rem 1fr; gap: 0.5rem; align-items: center; font-size: 0.75rem; }
  .gantt-label { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .gantt-track { position: relative; height: 1.25rem; background: var(--color-surface); border-radius: var(--radius-sm); }
  .gantt-bar {
    position: absolute;
    top: 2px;
    bottom: 2px;
    background: var(--color-secondary);
    border-radius: 3px;
    min-width: 4px;
  }
</style>
