// 🧪 E2E test: Simulate VNPay /payments/webhook with HMAC-SHA512 signature
const { test, expect } = require('@playwright/test');
const crypto = require('crypto');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

function quotePlus(str) {
  return encodeURIComponent(String(str)).replace(/%20/g, '+');
}

function sortedQueryString(params) {
  const entries = Object.entries(params)
    .filter(([k, v]) => k !== 'vnp_SecureHash' && k !== 'vnp_SecureHashType' && v !== undefined && v !== null)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return entries.map(([k, v]) => `${k}=${quotePlus(v)}`).join('&');
}

function signParams(params, secret) {
  const data = sortedQueryString(params);
  const h = crypto.createHmac('sha512', Buffer.from(secret, 'utf-8'));
  h.update(Buffer.from(data, 'utf-8'));
  return h.digest('hex');
}

test('VNPay webhook: valid signature returns 200 with RspCode=00', async ({ request }) => {
  const secret = process.env.VNPAY_HASH_SECRET || 'secret';
  const now = new Date();
  const ts = `${now.getUTCFullYear()}${String(now.getUTCMonth()+1).padStart(2,'0')}${String(now.getUTCDate()).padStart(2,'0')}${String(now.getUTCHours()).padStart(2,'0')}${String(now.getUTCMinutes()).padStart(2,'0')}${String(now.getUTCSeconds()).padStart(2,'0')}`;
  const txnRef = `WEBHOOK${Date.now()}`;

  const params = {
    vnp_Version: '2.1.0',
    vnp_Command: 'pay',
    vnp_TmnCode: 'demo',
    vnp_Amount: String(10000),
    vnp_CurrCode: 'VND',
    vnp_TxnRef: txnRef,
    vnp_OrderInfo: 'FADO Webhook Test',
    vnp_ResponseCode: '00',
    vnp_CreateDate: ts,
  };

  const hash = signParams(params, secret);
  const signed = { ...params, vnp_SecureHash: hash };

  const res = await request.post(`${BACKEND_URL}/payments/webhook`, {
    data: signed,
    headers: { 'content-type': 'application/json' },
  });
  expect(res.status()).toBe(200);
  const data = await res.json();
  expect(data).toHaveProperty('RspCode', '00');
});

test('VNPay webhook: invalid signature returns 400', async ({ request }) => {
  const secret = process.env.VNPAY_HASH_SECRET || 'secret';
  const now = new Date();
  const ts = `${now.getUTCFullYear()}${String(now.getUTCMonth()+1).padStart(2,'0')}${String(now.getUTCDate()).padStart(2,'0')}${String(now.getUTCHours()).padStart(2,'0')}${String(now.getUTCMinutes()).padStart(2,'0')}${String(now.getUTCSeconds()).padStart(2,'0')}`;
  const txnRef = `WEBHOOK_BAD${Date.now()}`;

  const params = {
    vnp_Version: '2.1.0',
    vnp_Command: 'pay',
    vnp_TmnCode: 'demo',
    vnp_Amount: String(10000),
    vnp_CurrCode: 'VND',
    vnp_TxnRef: txnRef,
    vnp_OrderInfo: 'FADO Webhook Test Bad',
    vnp_ResponseCode: '00',
    vnp_CreateDate: ts,
  };

  // Tạo chữ ký đúng rồi sửa dữ liệu để phá chữ ký
  const goodHash = signParams(params, secret);
  const tampered = { ...params, vnp_SecureHash: goodHash, vnp_Amount: String(10001) };

  const res = await request.post(`${BACKEND_URL}/payments/webhook`, {
    data: tampered,
    headers: { 'content-type': 'application/json' },
  });
  expect(res.status()).toBe(400);
});
