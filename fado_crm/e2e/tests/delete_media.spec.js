// 🧪 E2E test: Delete media via API after UI upload
const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

async function loginAndSeed(page, request) {
  const loginRes = await request.post(`${BACKEND_URL}/auth/login`, {
    data: { email: 'admin@fado.vn', password: 'admin123' },
    headers: { 'Content-Type': 'application/json' }
  });
  if (loginRes.status() !== 200) {
    test.skip(true, 'Admin login failed; ensure backend is running and admin exists');
    return null;
  }
  const loginData = await loginRes.json();
  const { access_token, refresh_token, user } = loginData;
  await page.addInitScript(([a, r, u]) => {
    localStorage.setItem('access_token', a);
    localStorage.setItem('refresh_token', r);
    localStorage.setItem('user_info', JSON.stringify(u));
  }, [access_token, refresh_token, user]);
  return loginData;
}

const ONE_BY_ONE_PNG_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAoMBg1s2C5cAAAAASUVORK5CYII=';

// Upload then delete via API
test('delete uploaded product image via API', async ({ page, request }) => {
  const loginData = await loginAndSeed(page, request);
  if (!loginData) return; // skipped

  // Go to upload page
  await page.goto(`${FRONTEND_URL}/file-upload.html`);
  await expect(page.locator('#single')).toBeVisible();

  // Manually init uploader and upload one file
  await page.evaluate((b64) => {
    function base64ToUint8Array(base64) {
      const binary_string = atob(base64);
      const len = binary_string.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) bytes[i] = binary_string.charCodeAt(i);
      return bytes;
    }
    if (typeof FileUploadManager !== 'undefined' && !window.__testUploader) {
      window.__testUploader = new FileUploadManager();
    }
    const bytes = base64ToUint8Array(b64);
    const blob = new Blob([bytes], { type: 'image/png' });
    const file = new File([blob], 'to_delete.png', { type: 'image/png' });
    window.__testUploader.handleFiles([file], false);
    window.__testUploader.uploadAll();
  }, ONE_BY_ONE_PNG_BASE64);

  // Wait success UI
  await expect(page.locator('.upload-item .status-success')).toBeVisible({ timeout: 15000 });

  // Fetch latest uploaded filename via API
  const token = loginData.access_token;
  const listRes = await request.get(`${BACKEND_URL}/upload/list?category=product_images&limit=1`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  expect(listRes.status()).toBe(200);
  const listData = await listRes.json();
  expect(listData.items?.length).toBeGreaterThan(0);
  const filename = listData.items[0].filename;

  // Delete via API
  const delRes = await request.delete(`${BACKEND_URL}/upload/file?category=product_images&filename=${encodeURIComponent(filename)}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  expect(delRes.status()).toBe(200);

  // Confirm not present in top items (best-effort)
  const listAfter = await request.get(`${BACKEND_URL}/upload/list?category=product_images&limit=5`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  expect(listAfter.status()).toBe(200);
  const afterData = await listAfter.json();
  const names = (afterData.items || []).map(it => it.filename);
  expect(names).not.toContain(filename);
});
