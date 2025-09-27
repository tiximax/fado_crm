// 🧪 E2E tests: UI login for manager/staff/viewer via real browser
const { test, expect } = require('@playwright/test');

const FRONTEND_URL = 'http://127.0.0.1:3010';
const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8003';

async function seedRoleAndOpen(page, role, email) {
  // Seed tokens and user info before any page scripts run
  const jwt = require('jsonwebtoken');
  const SECRET = 'fado_crm_super_secret_key_2024_vietnam_rocks';
  const payload = { sub: email, role, type: 'access' };
  const access = jwt.sign(payload, SECRET, { algorithm: 'HS256', expiresIn: '30m' });
  await page.addInitScript((a, e, r) => {
    localStorage.setItem('access_token', a);
    localStorage.setItem('refresh_token', 'dev-refresh');
    localStorage.setItem('user_info', JSON.stringify({ email: e, ho_ten: e, vai_tro: r, is_active: true }));
  }, access, email, role);
  await page.goto(`${FRONTEND_URL}/index.html`);
}

async function loginSeedTokensAndOpen(page, request, email, password) {
  // Seed tokens via API or manual JWT before loading index.html
  const loginRes = await request.post(`${BACKEND_URL}/auth/login`, {
    data: { email, password },
    headers: { 'Content-Type': 'application/json' }
  });

  if (loginRes.status() === 200) {
    const data = await loginRes.json();
    const { access_token, refresh_token, user } = data;
    await page.addInitScript(([a, r, u]) => {
      localStorage.setItem('access_token', a);
      localStorage.setItem('refresh_token', r);
      localStorage.setItem('user_info', JSON.stringify(u));
    }, [access_token, refresh_token, user]);
  } else {
    const jwt = require('jsonwebtoken');
    const SECRET = 'fado_crm_super_secret_key_2024_vietnam_rocks';
    const payload = { sub: email, role: email.split('@')[0], type: 'access' };
    const access = jwt.sign(payload, SECRET, { algorithm: 'HS256', expiresIn: '30m' });
    await page.addInitScript((a, e) => {
      localStorage.setItem('access_token', a);
      localStorage.setItem('refresh_token', 'dev-refresh');
      localStorage.setItem('user_info', JSON.stringify({ email: e, ho_ten: e, vai_tro: e.split('@')[0], is_active: true }));
    }, access, email);
  }

  await page.goto(`${FRONTEND_URL}/index.html`);
}

async function assertCommonPostLogin(page) {
  // Wait for app name in navbar
  await expect(page.locator('#appName')).toBeVisible({ timeout: 15000 });
  // Non-admins should NOT see admin-only buttons
  await expect(page.locator('button.admin-only[data-tab="system-settings"]')).toBeHidden();
  await expect(page.locator('button.admin-only[data-tab="users"]')).toBeHidden();
}

async function assertRoleInStorage(page, expectedRole) {
  await expect(async () => {
    const role = await page.evaluate(() => {
      try {
        const u = JSON.parse(localStorage.getItem('user_info'));
        return u && u.vai_tro;
      } catch (e) {
        return null;
      }
    });
    expect(role).toBe(expectedRole);
  }).toPass();
}

// Manager login
async function loginViaForm(page, email, password) {
  await page.addInitScript((api) => { try { localStorage.setItem('api_base', api); } catch (e) {} }, BACKEND_URL);
  await page.goto(`${FRONTEND_URL}/login.html`);
  await page.locator('#email').fill(email);
  await page.locator('#password').fill(password);
  await page.getByRole('button', { name: /Đăng Nhập/i }).click();
  await page.waitForURL('**/index.html', { timeout: 20000 });
}

test('UI role login: manager (form) shows non-admin UI', async ({ page }) => {
  await loginViaForm(page, 'manager@fado.vn', 'manager123');
  await assertCommonPostLogin(page);
  await assertRoleInStorage(page, 'manager');
});

// Staff login
test('UI role login: staff (form) shows non-admin UI', async ({ page }) => {
  await loginViaForm(page, 'staff@fado.vn', 'staff123');
  await assertCommonPostLogin(page);
  await assertRoleInStorage(page, 'staff');
});

// Viewer login
test('UI role login: viewer (form) shows non-admin UI', async ({ page }) => {
  await loginViaForm(page, 'viewer@fado.vn', 'viewer123');
  await assertCommonPostLogin(page);
  await assertRoleInStorage(page, 'viewer');
});
