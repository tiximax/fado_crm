// Playwright config for FADO CRM E2E
// Frontend served at http://localhost:3000, Backend at http://localhost:8000

const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30_000,
  use: {
    headless: true,
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
    baseURL: 'http://localhost:3000'
  },
  reporter: [['list']]
});
