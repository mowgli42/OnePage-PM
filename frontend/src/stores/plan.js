import { get, writable } from 'svelte/store'

const API = '/_/backend'

/** Default plan when API is unavailable or file is missing (must match backend shape). */
export const defaultPlan = {
  projectId: null,
  projectNumber: null,
  header: { projectTitle: 'Regional Data Collection Pilot', sponsor: 'NASS Field Operations', projectManager: 'Jane Smith', startDate: 'Jan 1, 2026', endDate: 'Dec 31, 2026', reportingPeriod: 'FY Q2 2026', version: 'v1.0', dateUpdated: 'Feb 19, 2026' },
  quarters: ['Q1 2026', 'Q2 2026', 'Q3 2026', 'Q4 2026'],
  objectives: [
    { id: 'O1', title: 'Launch pilot in 3 regions', metric: '3/3 regions operational', owner: 'MS' },
    { id: 'O2', title: 'Complete baseline report', metric: 'Report approved', owner: 'JP' },
    { id: 'O3', title: 'Establish QA process (95% pass)', metric: '95% pass rate', owner: 'RK' },
    { id: 'O4', title: 'Train 20 field staff', metric: '20 certified', owner: 'MS' },
    { id: 'O5', title: 'Integrate data into national system', metric: 'API live', owner: 'TL' },
    { id: 'O6', title: 'Publish lessons learned', metric: 'Document released', owner: 'JS' },
  ],
  matrix: [
    [{ symbol: '○', label: 'Kickoff' }, { symbol: '●', label: 'Pilot start' }, { symbol: '●', label: '3 regions' }, { symbol: '○', label: 'Handoff' }],
    [{ symbol: '○', label: 'Scoping' }, { symbol: '○', label: 'Analysis' }, { symbol: '●', label: 'Draft' }, { symbol: '●', label: 'Approved' }],
    [{ symbol: '△', label: 'Design QA' }, { symbol: '○', label: 'Build' }, { symbol: '○', label: 'Test' }, { symbol: '●', label: '95% pass' }],
    [{ symbol: '○', label: 'Curriculum' }, { symbol: '●', label: 'Week 1–2' }, { symbol: '●', label: 'Week 3–4' }, { symbol: '○', label: 'Certify' }],
    [{ symbol: '○', label: 'Specs' }, { symbol: '○', label: 'Dev' }, { symbol: '△', label: 'UAT' }, { symbol: '●', label: 'Live' }],
    [{ symbol: '', label: '' }, { symbol: '', label: '' }, { symbol: '○', label: 'Draft' }, { symbol: '●', label: 'Release' }],
  ],
  owners: [
    { initials: 'JS', role: 'Project Manager' },
    { initials: 'JP', role: 'Lead Analyst' },
    { initials: 'MS', role: 'Field Coordinator' },
    { initials: 'RK', role: 'QA Lead' },
    { initials: 'TL', role: 'Systems Integrator' },
  ],
  budget: { total: 170000, spent: 38300, categories: [{ name: 'Personnel', planned: 120000, spent: 35000 }, { name: 'Travel', planned: 15000, spent: 2100 }, { name: 'Contracts', planned: 25000, spent: 0 }, { name: 'Other', planned: 10000, spent: 1200 }] },
  risks: [
    { text: 'Region 3 staffing gap', owner: 'MS', mitigation: 'Backup contractor identified' },
    { text: 'Data integration delay', owner: 'TL', mitigation: 'Early API testing in Q2' },
    { text: 'Budget overrun risk', owner: 'JS', mitigation: '10% contingency held' },
  ],
  kpis: [
    { label: 'Surveys completed', value: '250 / 400', target: true },
    { label: 'Data quality pass rate', value: '92%', target: false },
    { label: 'Staff trained', value: '18 / 20', target: true },
    { label: 'Deliverables on time', value: '4 / 5', target: true },
  ],
  status: { level: 'yellow', text: 'Region 3 data collection delayed 2 weeks; mitigation in progress.' },
}

export const plan = writable(null)
export const planLoading = writable(false)
export const planSaving = writable(false)
export const planError = writable(null)
export const oppmEditing = writable(false)
/** List of { id, title } from GET /plans */
export const plansList = writable([])
/** Currently selected plan id (for multi-plan). */
export const currentPlanId = writable(null)

export async function fetchPlans() {
  try {
    const res = await fetch(`${API}/plans`)
    if (!res.ok) return
    const list = await res.json()
    plansList.set(Array.isArray(list) ? list : [])
    if (list?.length && !get(currentPlanId)) currentPlanId.set(list[0].id)
    return list
  } catch (_) {
    plansList.set([])
    return []
  }
}

export async function fetchPlan(planId = null) {
  planLoading.set(true)
  planError.set(null)
  const id = planId ?? get(currentPlanId)
  try {
    const url = id ? `${API}/plan?plan_id=${encodeURIComponent(id)}` : `${API}/plan`
    const res = await fetch(url)
    const data = res.ok ? await res.json() : null
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    if (id) currentPlanId.set(id)
    plan.set(data)
    return data
  } catch (e) {
    planError.set(e.message)
    plan.set(null)
    return null
  } finally {
    planLoading.set(false)
  }
}

export async function savePlan(planData, planId = null) {
  planSaving.set(true)
  planError.set(null)
  const id = planId ?? get(currentPlanId)
  try {
    const url = id ? `${API}/plan?plan_id=${encodeURIComponent(id)}` : `${API}/plan`
    const res = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planData),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    plan.set(data)
    return data
  } catch (e) {
    planError.set(e.message)
    throw e
  } finally {
    planSaving.set(false)
  }
}
