// 🧪 E2E test: Simulate VNPay /payments/return with HMAC-SHA512 signature
const { test, expect } = require('@playwright/test');
const crypto = require('crypto');

const BACKEND_URL = 'http://localhost:8000';

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

test('simulate VNPay return: expect 200 and status processed', async ({ request }) => {
  const secret = process.env.VNPAY_HASH_SECRET || 'secret';
  const now = new Date();
  const ts = `${now.getUTCFullYear()}${String(now.getUTCMonth()+1).padStart(2,'0')}${String(now.getUTCDate()).padStart(2,'0')}${String(now.getUTCHours()).padStart(2,'0')}${String(now.getUTCMinutes()).padStart(2,'0')}${String(now.getUTCSeconds()).padStart(2,'0')}`;
  const txnRef = `TEST${Date.now()}`;

  const params = {
    vnp_Version: '2.1.0',
    vnp_Command: 'pay',
    vnp_TmnCode: 'demo',
    vnp_Amount: String(10000),
    vnp_CurrCode: 'VND',
    vnp_TxnRef: txnRef,
    vnp_OrderInfo: 'FADO Test Return',
    vnp_ResponseCode: '00',
    vnp_CreateDate: ts,
  };

  const hash = signParams(params, secret);
  const signed = { ...params, vnp_SecureHash: hash };
  const qs = Object.entries(signed)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
    .join('&');

  const res = await request.get(`${BACKEND_URL}/payments/return?${qs}`);
  expect(res.status()).toBe(200);
  const data = await res.json();
  expect(data).toHaveProperty('success', true);
  expect(data).toHaveProperty('status');
  // With ResponseCode=00 we expect success
  expect(data.status).toBe('success');
  expect(data.txn_ref).toBe(txnRef);
});
