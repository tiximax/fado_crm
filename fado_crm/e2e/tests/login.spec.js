// 🧪 E2E test: UI login via real browser and form submission
const { test, expect } = require('@playwright/test');

const FRONTEND_URL = 'http://127.0.0.1:3010';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Helper: ensure backend health
async function ensureBackendHealthy(request) {
  const res = await request.get(`${BACKEND_URL}/health`);
  expect(res.status()).toBe(200);
}

// UI login test using the login form
test('UI login via form succeeds', async ({ page, request }) => {
  await ensureBackendHealthy(request);

  // Go to login page
  await page.goto(`${FRONTEND_URL}/login.html`);

  // Fill credentials
  await page.locator('#email').fill('admin@fado.vn');
  await page.locator('#password').fill('admin123');

  // Submit
  await page.getByRole('button', { name: /Đăng Nhập/i }).click();

  // Expect redirect to index.html
  await page.waitForURL('**/index.html', { timeout: 10000 });

  // Verify dashboard loaded (authenticated content)
  await expect(page.locator('#total-customers')).toBeVisible({ timeout: 15000 });
});
