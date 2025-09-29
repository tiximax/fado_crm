# -*- coding: utf-8 -*-
"""
VNPay Payment Gateway Integration - cleaned version
Provides helpers: sign_params, verify_signature, build_payment_url
and a minimal VNPayGateway stub used by other parts of the app.
"""

import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# ---------- Low-level helpers (match Playwright tests) ----------
EXCLUDED_FIELDS = {"vnp_SecureHash", "vnp_SecureHashType"}


def _sorted_query_string(params: Dict[str, Any]) -> str:
    items = [(k, v) for k, v in params.items() if k not in EXCLUDED_FIELDS and v is not None]
    items.sort(key=lambda kv: kv[0])
    return "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in items)


def sign_params(params: Dict[str, Any], secret: str) -> str:
    data = _sorted_query_string(params)
    h = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha512)
    return h.hexdigest()


def verify_signature(query_params: Dict[str, Any], secret: str) -> bool:
    provided = str(query_params.get("vnp_SecureHash", "")).lower()
    calculated = sign_params(query_params, secret).lower()
    return provided == calculated


def build_payment_url(params: Dict[str, Any], secret: str, pay_url: str) -> str:
    secure_hash = sign_params(params, secret)
    signed = dict(params)
    signed["vnp_SecureHash"] = secure_hash
    query = _sorted_query_string(signed)
    if "vnp_SecureHash=" not in query:
        query = f"{query}&vnp_SecureHash={urllib.parse.quote_plus(secure_hash)}"
    return f"{pay_url}?{query}"


# ---------- Minimal gateway (subset) ----------
class VNPayGateway:
    def __init__(self, merchant_id: str, secret_key: str, is_sandbox: bool = True):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.is_sandbox = is_sandbox
        if is_sandbox:
            self.payment_url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
        else:
            self.payment_url = "https://vnpayment.vn/paymentv2/vpcpay.html"
        self.version = "2.1.0"
        self.command = "pay"
        self.currency_code = "VND"
        self.locale = "vn"

    def create_payment_url(
        self, order_data: Dict[str, Any], return_url: str, ipn_url: Optional[str] = None
    ) -> Dict[str, Any]:
        required = ["order_id", "amount", "description"]
        for f in required:
            if f not in order_data:
                raise ValueError(f"Missing required field: {f}")
        txn_ref = f"FADO_{order_data['order_id']}_{int(datetime.now().timestamp())}"
        vnp_params = {
            "vnp_Version": self.version,
            "vnp_Command": self.command,
            "vnp_TmnCode": self.merchant_id,
            "vnp_Amount": str(int(order_data["amount"] * 100)),
            "vnp_CurrCode": self.currency_code,
            "vnp_TxnRef": txn_ref,
            "vnp_OrderInfo": order_data.get("description", ""),
            "vnp_OrderType": order_data.get("order_type", "other"),
            "vnp_Locale": order_data.get("locale", self.locale),
            "vnp_ReturnUrl": return_url,
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }
        url = build_payment_url(vnp_params, self.secret_key, self.payment_url)
        return {"success": True, "payment_url": url, "transaction_ref": txn_ref}

    def get_supported_banks(self) -> List[Dict[str, str]]:
        return [
            {"code": "VIETCOMBANK", "name": "Vietcombank", "type": "atm"},
            {"code": "VIETINBANK", "name": "VietinBank", "type": "atm"},
            {"code": "BIDV", "name": "BIDV", "type": "atm"},
        ]


# Factory


def create_vnpay_gateway(
    merchant_id: str = None, secret_key: str = None, is_sandbox: bool = True
) -> VNPayGateway:
    merchant_id = merchant_id or "FADO001"
    secret_key = secret_key or "FADOSECRETKEY123456789"
    return VNPayGateway(merchant_id, secret_key, is_sandbox)
