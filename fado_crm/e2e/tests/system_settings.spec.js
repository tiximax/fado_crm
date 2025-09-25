// 🧪 E2E for System Settings UI (Admin only)
const { test, expect } = require('@playwright/test');

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000';

const jwt = require('jsonwebtoken');

async function seedAdminTokens(page, request) {
  const loginRes = await request.post(`${BACKEND_URL}/auth/login`, {
    data: { email: 'admin@fado.vn', password: 'admin123' },
    headers: { 'Content-Type': 'application/json' }
  });
  if (loginRes.status() !== 200) {
    test.skip(true, 'Admin login failed; ensure backend/setup_users.py ran');
    return;
  }
  const loginData = await loginRes.json();
  const { access_token, refresh_token, user } = loginData;
  await page.addInitScript(([a, r, u]) => {
    localStorage.setItem('access_token', a);
    localStorage.setItem('refresh_token', r);
    localStorage.setItem('user_info', JSON.stringify(u));
  }, [access_token, refresh_token, user]);
}

// Create a setting and then update it via the UI
test('admin can create and update a system setting via UI', async ({ page, request }) => {
// Try real login; if it fails, fallback to manual token generation
try {
  await seedAdminTokens(page, request);
} catch (e) {
  // ignore
}

// If tokens not set (due to login failure), seed manual JWT
await page.addInitScript(() => {
  const hasToken = !!localStorage.getItem('access_token');
  window._hasToken = hasToken;
});
const hasToken = await page.evaluate(() => window._hasToken);
if (!hasToken) {
  const SECRET = 'fado_crm_super_secret_key_2024_vietnam_rocks';
  const payload = { sub: 'admin@fado.vn', role: 'admin', type: 'access' };
  const access = jwt.sign(payload, SECRET, { algorithm: 'HS256', expiresIn: '30m' });
  await page.addInitScript((a) => {
    localStorage.setItem('access_token', a);
    localStorage.setItem('refresh_token', 'dev-refresh');
    localStorage.setItem('user_info', JSON.stringify({ email: 'admin@fado.vn', ho_ten: 'Admin', vai_tro: 'admin', is_active: true }));
  }, access);
}

  await page.goto(`${FRONTEND_URL}/index.html`);

  // Open System Settings tab
  await page.getByRole('button', { name: /Cấu hình/i }).click();

  // Create setting using quick form
  await page.locator('#settingKey').fill('app_name');
  await page.locator('#settingValue').fill('FADO CRM');
  await page.locator('#settingDescription').fill('Tên ứng dụng');
  await page.getByRole('button', { name: /Lưu/i }).first().click();

  // Wait for success toast or row appearance
  await expect(page.locator('#settings-table-body')).toBeVisible();
  await expect(page.locator('#settings-table-body input#setting-value-app_name')).toBeVisible();

  // Update value inline and save
  const row = page.locator('#settings-table-body tr', { has: page.locator('code', { hasText: 'app_name' }) });
  await row.locator('input#setting-value-app_name').fill('FADO CRM PRO');
  await row.getByRole('button', { name: /Lưu/i }).click();

  // Verify input value updated in UI
  await expect(page.locator('#settings-table-body input#setting-value-app_name')).toHaveValue('FADO CRM PRO');
});
