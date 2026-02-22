/** @type {import('@playwright/test').PlaywrightTestConfig} */
export default {
  testDir: 'e2e',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  webServer: process.env.CI
    ? undefined
    : {
        command: 'npm run dev',
        url: 'http://localhost:5173',
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
      },
  timeout: 15000,
  expect: { timeout: 5000 },
}
