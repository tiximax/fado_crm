// 🧪 E2E test: Upload product image via UI (Local storage driver)
const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

async function seedAdminTokens(page, request) {
  const loginRes = await request.post(`${BACKEND_URL}/auth/login`, {
    data: { email: 'admin@fado.vn', password: 'admin123' },
    headers: { 'Content-Type': 'application/json' }
  });
  if (loginRes.status() !== 200) {
    test.skip(true, 'Admin login failed; ensure backend is running and admin exists');
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

// Minimal 1x1 PNG image (transparent)
const ONE_BY_ONE_PNG_BASE64 =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAoMBg1s2C5cAAAAASUVORK5CYII=';

// Test upload single image and verify success status in UI
test('upload single product image via UI succeeds', async ({ page, request }) => {
  // Seed tokens so file-upload page doesn't redirect to login
  await seedAdminTokens(page, request);

  // Go to file upload page
  await page.goto(`${FRONTEND_URL}/file-upload.html`);

  // Ensure auth recognized
  await page.waitForFunction(() => window.isAuthenticated && window.isAuthenticated());

  // Ensure single tab content visible and drop area ready
  await expect(page.locator('#single')).toBeVisible();
  await expect(page.locator('#singleDropArea')).toBeVisible();

  // Manually initialize uploader if DOMContentLoaded handler didn't (edge cases)
  await page.evaluate(() => {
    try {
      if (typeof FileUploadManager !== 'undefined' && !window.__testUploader) {
        window.__testUploader = new FileUploadManager();
      }
    } catch (e) {
      // ignore
    }
  });

  // Add a File programmatically and trigger upload via the uploader instance
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
    const file = new File([blob], 'tiny.png', { type: 'image/png' });
    // Add to queue and upload
    window.__testUploader.handleFiles([file], false);
    window.__testUploader.uploadAll();
  }, ONE_BY_ONE_PNG_BASE64);

  // Expect the queued item to appear and then succeed
  await expect(page.locator('#uploadQueue')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('.upload-item')).toBeVisible({ timeout: 10000 });

  // Wait for success status
  await expect(page.locator('.upload-item .status-success')).toBeVisible({ timeout: 15000 });

  // Expect the queued item to show success status
  await expect(page.locator('.upload-item .status-success')).toBeVisible({ timeout: 15000 });
});
