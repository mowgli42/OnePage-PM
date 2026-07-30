/**
 * E2E tests for the app workflow using mock data.
 * Backend must be running at http://localhost:8000 (start separately).
 * Run: npx playwright test (or npm run test:e2e)
 */
import { test, expect } from '@playwright/test'

const API = process.env.API_URL || 'http://localhost:8000'

test.describe('App workflow', () => {
  test('Todos view loads and shows list', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('.app')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('h1')).toContainText('Project Management')
    await expect(page.locator('button.tab:has-text("Todos")')).toBeVisible()
    await expect(page.locator('button.tab:has-text("OPPM")')).toBeVisible()
  })

  test('OPPM view loads and shows plan', async ({ page }) => {
    await page.goto('/?view=oppm')
    await expect(page.locator('.oppm')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('.oppm-project-title')).toBeVisible()
    await expect(page.locator('.oppm-header')).toBeVisible()
    await expect(page.locator('.oppm-matrix')).toBeVisible()
  })

  test('Edit plan opens panel and shows schedule sections', async ({ page }) => {
    await page.goto('/?view=oppm')
    await expect(page.locator('.oppm')).toBeVisible({ timeout: 10000 })
    // Header control is icon-only; match accessible name (aria-label)
    await page.getByRole('button', { name: 'Edit plan' }).click()
    await expect(page.locator('.edit-panel')).toBeVisible()
    await expect(page.locator('.edit-panel h3')).toContainText('Edit project plan')
    await expect(page.locator('.edit-section h4', { hasText: 'Schedule – Time periods' })).toBeVisible()
    await expect(page.locator('.edit-section h4', { hasText: 'Schedule – Objectives' })).toBeVisible()
    await expect(page.locator('.edit-section h4', { hasText: 'Schedule – Matrix' })).toBeVisible()
  })

  test('Save plan persists and reload shows data', async ({ page, request }) => {
    const mockPlan = {
      header: {
        projectTitle: 'E2E Test Project',
        sponsor: 'E2E Sponsor',
        projectManager: 'Test PM',
        startDate: '2026-01-01',
        endDate: '2026-12-31',
        reportingPeriod: 'Q1 2026',
        version: 'v1',
        dateUpdated: 'Feb 22, 2026',
      },
      quarters: ['Q1 2026', 'Q2 2026'],
      objectives: [{ id: 'O1', title: 'E2E objective', metric: 'Done', owner: 'XX' }],
      matrix: [[{ symbol: '●', label: 'Done' }, { symbol: '', label: '' }]],
      owners: [{ initials: 'XX', role: 'Tester' }],
      budget: { total: 1000, spent: 0, categories: [{ name: 'X', planned: 1000, spent: 0 }] },
      risks: [],
      kpis: [],
      status: { level: 'green', text: 'E2E test.' },
    }

    // UI loads the first plan from GET /plans (typically plan_id=default), not legacy /plan alone
    const plansRes = await request.get(`${API}/plans`)
    expect(plansRes.ok()).toBeTruthy()
    const plans = await plansRes.json()
    const planId = plans?.[0]?.id || 'default'
    const putRes = await request.put(`${API}/plan?plan_id=${encodeURIComponent(planId)}`, {
      data: mockPlan,
    })
    expect(putRes.ok()).toBeTruthy()

    await page.goto('/?view=oppm')
    await expect(page.locator('.oppm')).toBeVisible({ timeout: 10000 })
    await expect(page.locator('.oppm-project-title')).toContainText('E2E Test Project')
    await expect(page.locator('.oppm-header')).toContainText('E2E Sponsor')
    await expect(page.locator('.oppm-matrix')).toContainText('E2E objective')
  })
})
