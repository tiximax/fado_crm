// 🧪 FADO CRM - E2E smoke tests
const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Basic server health
test('backend health endpoint responds', async ({ request }) => {
  const res = await request.get(`${BACKEND_URL}/health`);
  expect(res.status()).toBe(200);
  const data = await res.json();
  expect(data).toHaveProperty('status');
});

// Login page loads
test('login page loads with form', async ({ page }) => {
  await page.goto(`${FRONTEND_URL}/login.html`);
  await expect(page.getByRole('button', { name: /Đăng Nhập/i })).toBeVisible();
  await expect(page.locator('input#email')).toBeVisible();
  await expect(page.locator('input#password')).toBeVisible();
});

// Index requires authentication
test('index redirects to login when unauthenticated', async ({ page }) => {
  await page.goto(`${FRONTEND_URL}/index.html`);
  await page.waitForURL('**/login.html');
  expect(page.url()).toContain('login.html');
});

// Authenticated dashboard (optional if demo users exist)
test('dashboard loads when tokens are present (optional)', async ({ page, request }) => {
  // Attempt to login via API using demo admin credentials
  const loginRes = await request.post(`${BACKEND_URL}/auth/login`, {
    data: { email: 'admin@fado.vn', password: 'admin123' },
    headers: { 'Content-Type': 'application/json' }
  });

  if (loginRes.status() !== 200) {
    test.skip(true, 'Demo users not available, skipping authenticated test');
    return;
  }

  const loginData = await loginRes.json();
  const { access_token, refresh_token, user } = loginData;

  // Seed localStorage with tokens before any page scripts run
  await page.addInitScript(([a, r, u]) => {
    localStorage.setItem('access_token', a);
    localStorage.setItem('refresh_token', r);
    localStorage.setItem('user_info', JSON.stringify(u));
  }, [access_token, refresh_token, user]);

  await page.goto(`${FRONTEND_URL}/index.html`);

  // Expect dashboard header or stats to be visible
  await expect(page.locator('#total-customers')).toBeVisible();
});
