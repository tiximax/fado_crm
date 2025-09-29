import hashlib
import hmac
import time
import urllib.parse

import requests

BACKEND = "http://127.0.0.1:8003"
secret = "secret"
now = time.gmtime()
ts = f"{now.tm_year}{now.tm_mon:02d}{now.tm_mday:02d}{now.tm_hour:02d}{now.tm_min:02d}{now.tm_sec:02d}"
txnRef = f"TEST{int(time.time()*1000)}"
params = {
    "vnp_Version": "2.1.0",
    "vnp_Command": "pay",
    "vnp_TmnCode": "demo",
    "vnp_Amount": str(10000),
    "vnp_CurrCode": "VND",
    "vnp_TxnRef": txnRef,
    "vnp_OrderInfo": "FADO Test Return",
    "vnp_ResponseCode": "00",
    "vnp_CreateDate": ts,
}
EXCLUDED = {"vnp_SecureHash", "vnp_SecureHashType"}
items = sorted([(k, v) for k, v in params.items() if k not in EXCLUDED])
base = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in items)
h = hmac.new(secret.encode(), base.encode(), hashlib.sha512).hexdigest()
params_signed = dict(params)
params_signed["vnp_SecureHash"] = h
qs = "&".join(
    f"{urllib.parse.quote(k)}={urllib.parse.quote(str(v))}" for k, v in params_signed.items()
)
url = f"{BACKEND}/payments/return?{qs}"
print("GET", url)
r = requests.get(url)
print("Status", r.status_code)
print("Body", r.text)
