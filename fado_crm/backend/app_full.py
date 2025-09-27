# -*- coding: utf-8 -*-
# FADO CRM - Full Application (app_full)
# Hợp nhất server ổn định cho dev/test (auth + dashboard + CRUD cơ bản) + một số module nâng cao

from main_working import app  # Tái sử dụng toàn bộ app đã ổn định trong main_working

# ===== Advanced Modules: Minimal Payments (VNPay) =====
from fastapi import HTTPException, Request
from typing import Dict, Any
import hmac
import hashlib
import urllib.parse
import os

EXCLUDED_FIELDS = {"vnp_SecureHash", "vnp_SecureHashType"}

def _sorted_query_string(params: Dict[str, Any]) -> str:
    items = [(k, v) for k, v in params.items() if k not in EXCLUDED_FIELDS and v is not None]
    items.sort(key=lambda kv: kv[0])
    return "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in items)

def _sign_params(params: Dict[str, Any], secret: str) -> str:
    data = _sorted_query_string(params)
    return hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha512).hexdigest()

@app.get("/payments/return")
async def vnpay_return(request: Request):
    try:
        params = dict(request.query_params)
        secret = os.getenv("VNPAY_HASH_SECRET", "secret")
        provided = str(params.get("vnp_SecureHash", "")).lower()
        calculated = _sign_params(params, secret).lower()
        if provided != calculated:
            raise HTTPException(status_code=400, detail="Chu ky khong hop le")
        txn_ref = params.get("vnp_TxnRef")
        resp_code = params.get("vnp_ResponseCode")
        status = "success" if resp_code == "00" else "failed"
        return {"success": True, "status": status, "txn_ref": txn_ref}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loi xu ly return: {e}")

@app.post("/payments/webhook")
async def vnpay_webhook(payload: Dict[str, Any], request: Request):
    try:
        data: Dict[str, Any] = payload or {}
        if not data and request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            data = dict(form)
        secret = os.getenv("VNPAY_HASH_SECRET", "secret")
        provided = str(data.get("vnp_SecureHash", "")).lower()
        calculated = _sign_params(data, secret).lower()
        if provided != calculated:
            raise HTTPException(status_code=400, detail="Chu ky khong hop le")
        return {"RspCode": "00", "Message": "Confirm Success"}
    except HTTPException:
        raise
    except Exception as e:
        return {"RspCode": "99", "Message": f"system error: {e}"}
