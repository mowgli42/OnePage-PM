#!/usr/bin/env node
/**
 * Capture screenshots for README walkthrough.
 * Run: npm run screenshot (with frontend dev server and backend running)
 * Or: npm run screenshot -- --standalone (starts servers, captures, exits)
 */
import { chromium } from 'playwright'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import { spawn } from 'child_process'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = join(__dirname, '../..')
const outDir = join(root, 'docs/screenshots')

const BASE = process.env.BASE_URL || 'http://localhost:5173'

async function capture() {
  const browser = await chromium.launch()
  const page = await browser.newPage()

  await page.setViewportSize({ width: 1280, height: 800 })

  try {
    await page.goto(BASE, { waitUntil: 'networkidle', timeout: 10000 })
  } catch (e) {
    console.error('Could not reach', BASE, '- start dev server with: cd frontend && npm run dev')
    await browser.close()
    process.exit(1)
  }

  const fs = await import('fs')
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true })

  // Screenshot 1: Todos view (default)
  await page.waitForSelector('.app', { timeout: 5000 })
  await page.screenshot({ path: join(outDir, '01-todos-view.png'), fullPage: false })
  console.log('Saved 01-todos-view.png')

  // Switch to OPPM tab
  await page.click('button.tab:has-text("OPPM")')
  await page.waitForSelector('.oppm', { timeout: 3000 })

  // Screenshot 2: OPPM full view
  await page.screenshot({ path: join(outDir, '02-oppm-full.png'), fullPage: true })
  console.log('Saved 02-oppm-full.png')

  // Screenshot 3: OPPM matrix only (scrolled)
  await page.screenshot({ path: join(outDir, '03-oppm-matrix.png'), fullPage: false })
  console.log('Saved 03-oppm-matrix.png')

  await browser.close()
}

capture().catch((e) => {
  console.error(e)
  process.exit(1)
})
