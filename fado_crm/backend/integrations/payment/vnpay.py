import hmac
import hashlib
import urllib.parse
from typing import Dict, Tuple, List

# VNPay helpers: sign, build URL, verify

EXCLUDED_FIELDS = {"vnp_SecureHash", "vnp_SecureHashType"}


def _sorted_query_string(params: Dict[str, str]) -> str:
    items = [(k, v) for k, v in params.items() if k not in EXCLUDED_FIELDS and v is not None]
    items.sort(key=lambda kv: kv[0])
    return "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in items)


def sign_params(params: Dict[str, str], secret: str) -> str:
    data = _sorted_query_string(params)
    h = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.sha512)
    return h.hexdigest()


def build_payment_url(params: Dict[str, str], secret: str, pay_url: str) -> str:
    secure_hash = sign_params(params, secret)
    signed = dict(params)
    signed["vnp_SecureHash"] = secure_hash
    query = _sorted_query_string(signed)
    # include vnp_SecureHash at the end as VNPay expects
    if "vnp_SecureHash=" not in query:
        query = f"{query}&vnp_SecureHash={urllib.parse.quote_plus(secure_hash)}"
    return f"{pay_url}?{query}"


def verify_signature(query_params: Dict[str, str], secret: str) -> bool:
    provided = query_params.get("vnp_SecureHash", "").lower()
    calculated = sign_params(query_params, secret).lower()
    return provided == calculated

# -*- coding: utf-8 -*-
"""
VNPay Payment Gateway Integration
Tích hợp thanh toán VNPay cho FADO CRM - Gateway phổ biến nhất Việt Nam
"""

import hashlib
import hmac
import urllib.parse
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import json
import uuid

from logging_config import app_logger


class VNPayGateway:
    """VNPay Payment Gateway Integration"""

    def __init__(self, merchant_id: str, secret_key: str, is_sandbox: bool = True):
        self.merchant_id = merchant_id
        self.secret_key = secret_key
        self.is_sandbox = is_sandbox

        # VNPay URLs
        if is_sandbox:
            self.payment_url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
            self.api_url = "https://sandbox.vnpayment.vn/merchant_webapi/api"
        else:
            self.payment_url = "https://vnpayment.vn/paymentv2/vpcpay.html"
            self.api_url = "https://vnpayment.vn/merchant_webapi/api"

        # Default configuration
        self.version = "2.1.0"
        self.command = "pay"
        self.currency_code = "VND"
        self.locale = "vn"

        app_logger.info(f"🏦 VNPay Gateway initialized - {'Sandbox' if is_sandbox else 'Production'}")

    def create_payment_url(self, order_data: Dict[str, Any], return_url: str,
                          ipn_url: Optional[str] = None) -> Dict[str, Any]:
        """🔗 Tạo URL thanh toán VNPay"""

        try:
            # Validate required fields
            required_fields = ['order_id', 'amount', 'description']
            for field in required_fields:
                if field not in order_data:
                    raise ValueError(f"Missing required field: {field}")

            # Generate transaction reference
            txn_ref = f"FADO_{order_data['order_id']}_{int(datetime.now().timestamp())}"

            # Create order info
            order_info = f"Thanh toan don hang #{order_data['order_id']} - {order_data.get('description', 'FADO Order')}"

            # VNPay parameters
            vnp_params = {
                'vnp_Version': self.version,
                'vnp_Command': self.command,
                'vnp_TmnCode': self.merchant_id,
                'vnp_Amount': str(int(order_data['amount'] * 100)),  # VNPay expects amount in VND cents
                'vnp_CurrCode': self.currency_code,
                'vnp_TxnRef': txn_ref,
                'vnp_OrderInfo': order_info,
                'vnp_OrderType': order_data.get('order_type', 'other'),
                'vnp_Locale': order_data.get('locale', self.locale),
                'vnp_ReturnUrl': return_url,
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                'vnp_ExpireDate': (datetime.now() + timedelta(minutes=30)).strftime('%Y%m%d%H%M%S')
            }

            # Add IPN URL if provided
            if ipn_url:
                vnp_params['vnp_IpnUrl'] = ipn_url

            # Add customer info if available
            if 'customer' in order_data:
                customer = order_data['customer']
                if customer.get('phone'):
                    vnp_params['vnp_Bill_Mobile'] = customer['phone']
                if customer.get('email'):
                    vnp_params['vnp_Bill_Email'] = customer['email']
                if customer.get('full_name'):
                    vnp_params['vnp_Bill_FirstName'] = customer['full_name']
                if customer.get('address'):
                    vnp_params['vnp_Bill_Address'] = customer['address']

            # Generate secure hash
            vnp_params['vnp_SecureHash'] = self._generate_secure_hash(vnp_params)

            # Create payment URL
            payment_url = f"{self.payment_url}?{urllib.parse.urlencode(vnp_params)}"

            return {
                'success': True,
                'payment_url': payment_url,
                'transaction_ref': txn_ref,
                'amount': order_data['amount'],
                'currency': self.currency_code,
                'expires_at': vnp_params['vnp_ExpireDate'],
                'created_at': datetime.now().isoformat()
            }

        except Exception as e:
            app_logger.error(f"❌ Error creating VNPay payment URL: {str(e)}")
            return {
                'success': False,
                'error': f"Lỗi tạo URL thanh toán: {str(e)}"
            }

    def verify_payment_response(self, response_params: Dict[str, str]) -> Dict[str, Any]:
        """✅ Xác thực phản hồi từ VNPay"""

        try:
            # Extract secure hash from response
            received_hash = response_params.pop('vnp_SecureHash', '')

            if not received_hash:
                return {
                    'success': False,
                    'error': 'Missing secure hash in response'
                }

            # Generate expected hash
            expected_hash = self._generate_secure_hash(response_params)

            # Verify hash
            if not hmac.compare_digest(received_hash.upper(), expected_hash.upper()):
                app_logger.warning("🚨 VNPay payment hash verification failed")
                return {
                    'success': False,
                    'error': 'Invalid secure hash - possible tampering detected'
                }

            # Extract payment information
            transaction_status = response_params.get('vnp_TransactionStatus', '99')
            response_code = response_params.get('vnp_ResponseCode', '99')

            # Determine payment status
            is_successful = (response_code == '00' and transaction_status == '00')

            payment_info = {
                'success': True,
                'payment_successful': is_successful,
                'transaction_ref': response_params.get('vnp_TxnRef'),
                'amount': float(response_params.get('vnp_Amount', 0)) / 100,  # Convert back from cents
                'bank_code': response_params.get('vnp_BankCode'),
                'bank_transaction_id': response_params.get('vnp_BankTranNo'),
                'card_type': response_params.get('vnp_CardType'),
                'response_code': response_code,
                'transaction_status': transaction_status,
                'payment_date': response_params.get('vnp_PayDate'),
                'order_info': response_params.get('vnp_OrderInfo'),
                'gateway': 'vnpay',
                'verified_at': datetime.now().isoformat()
            }

            # Add status message
            payment_info['status_message'] = self._get_status_message(response_code)

            if is_successful:
                app_logger.info(f"✅ VNPay payment successful: {payment_info['transaction_ref']}")
            else:
                app_logger.warning(f"⚠️ VNPay payment failed: {payment_info['status_message']}")

            return payment_info

        except Exception as e:
            app_logger.error(f"❌ Error verifying VNPay payment: {str(e)}")
            return {
                'success': False,
                'error': f"Lỗi xác thực thanh toán: {str(e)}"
            }

    def query_transaction(self, transaction_ref: str, transaction_date: str) -> Dict[str, Any]:
        """🔍 Truy vấn thông tin giao dịch từ VNPay"""

        try:
            query_params = {
                'vnp_Version': self.version,
                'vnp_Command': 'querydr',
                'vnp_TmnCode': self.merchant_id,
                'vnp_TxnRef': transaction_ref,
                'vnp_OrderInfo': f'Query transaction {transaction_ref}',
                'vnp_TransactionDate': transaction_date,
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                'vnp_IpAddr': '127.0.0.1'
            }

            # Generate secure hash for query
            query_params['vnp_SecureHash'] = self._generate_secure_hash(query_params)

            # Make API request
            response = requests.post(
                f"{self.api_url}/transaction",
                data=query_params,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'transaction_status': result.get('vnp_TransactionStatus'),
                    'response_code': result.get('vnp_ResponseCode'),
                    'amount': float(result.get('vnp_Amount', 0)) / 100,
                    'bank_transaction_id': result.get('vnp_BankTranNo'),
                    'payment_date': result.get('vnp_PayDate'),
                    'queried_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'API request failed with status {response.status_code}'
                }

        except Exception as e:
            app_logger.error(f"❌ Error querying VNPay transaction: {str(e)}")
            return {
                'success': False,
                'error': f"Lỗi truy vấn giao dịch: {str(e)}"
            }

    def create_refund(self, original_transaction_ref: str, refund_amount: float,
                     reason: str, transaction_date: str) -> Dict[str, Any]:
        """💸 Tạo yêu cầu hoàn tiền VNPay"""

        try:
            refund_ref = f"RF_{original_transaction_ref}_{int(datetime.now().timestamp())}"

            refund_params = {
                'vnp_Version': self.version,
                'vnp_Command': 'refund',
                'vnp_TmnCode': self.merchant_id,
                'vnp_TransactionType': '03',  # Full refund
                'vnp_TxnRef': refund_ref,
                'vnp_Amount': str(int(refund_amount * 100)),
                'vnp_OrderInfo': f'Hoan tien {reason}',
                'vnp_TransactionNo': original_transaction_ref,
                'vnp_TransactionDate': transaction_date,
                'vnp_CreateBy': 'FADO_SYSTEM',
                'vnp_CreateDate': datetime.now().strftime('%Y%m%d%H%M%S'),
                'vnp_IpAddr': '127.0.0.1'
            }

            # Generate secure hash
            refund_params['vnp_SecureHash'] = self._generate_secure_hash(refund_params)

            # Make refund request
            response = requests.post(
                f"{self.api_url}/refund",
                data=refund_params,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                is_successful = result.get('vnp_ResponseCode') == '00'

                return {
                    'success': True,
                    'refund_successful': is_successful,
                    'refund_ref': refund_ref,
                    'original_transaction_ref': original_transaction_ref,
                    'refund_amount': refund_amount,
                    'response_code': result.get('vnp_ResponseCode'),
                    'response_message': result.get('vnp_Message'),
                    'created_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Refund API request failed with status {response.status_code}'
                }

        except Exception as e:
            app_logger.error(f"❌ Error creating VNPay refund: {str(e)}")
            return {
                'success': False,
                'error': f"Lỗi tạo hoàn tiền: {str(e)}"
            }

    def _generate_secure_hash(self, params: Dict[str, str]) -> str:
        """🔐 Tạo secure hash cho VNPay"""

        # Remove hash field if exists
        filtered_params = {k: v for k, v in params.items() if k != 'vnp_SecureHash'}

        # Sort parameters
        sorted_params = sorted(filtered_params.items())

        # Create query string
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])

        # Generate HMAC SHA512
        hash_value = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return hash_value.upper()

    def _get_status_message(self, response_code: str) -> str:
        """📝 Chuyển đổi response code thành message"""

        status_messages = {
            '00': 'Giao dịch thành công',
            '07': 'Trừ tiền thành công. Giao dịch bị nghi ngờ (liên quan tới lừa đảo, giao dịch bất thường).',
            '09': 'Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng chưa đăng ký dịch vụ InternetBanking tại ngân hàng.',
            '10': 'Giao dịch không thành công do: Khách hàng xác thực thông tin thẻ/tài khoản không đúng quá 3 lần',
            '11': 'Giao dịch không thành công do: Đã hết hạn chờ thanh toán. Xin quý khách vui lòng thực hiện lại giao dịch.',
            '12': 'Giao dịch không thành công do: Thẻ/Tài khoản của khách hàng bị khóa.',
            '13': 'Giao dịch không thành công do Quý khách nhập sai mật khẩu xác thực giao dịch (OTP).',
            '24': 'Giao dịch không thành công do: Khách hàng hủy giao dịch',
            '51': 'Giao dịch không thành công do: Tài khoản của quý khách không đủ số dư để thực hiện giao dịch.',
            '65': 'Giao dịch không thành công do: Tài khoản của Quý khách đã vượt quá hạn mức giao dịch trong ngày.',
            '75': 'Ngân hàng thanh toán đang bảo trì.',
            '79': 'Giao dịch không thành công do: KH nhập sai mật khẩu thanh toán quá số lần quy định.',
            '99': 'Các lỗi khác (lỗi còn lại, không có trong danh sách mã lỗi đã liệt kê)'
        }

        return status_messages.get(response_code, f'Lỗi không xác định (Code: {response_code})')

    def get_supported_banks(self) -> List[Dict[str, str]]:
        """🏪 Danh sách ngân hàng hỗ trợ"""

        return [
            {'code': 'VIETCOMBANK', 'name': 'Vietcombank', 'type': 'atm'},
            {'code': 'VIETINBANK', 'name': 'VietinBank', 'type': 'atm'},
            {'code': 'BIDV', 'name': 'BIDV', 'type': 'atm'},
            {'code': 'AGRIBANK', 'name': 'Agribank', 'type': 'atm'},
            {'code': 'TPB', 'name': 'TPBank', 'type': 'atm'},
            {'code': 'TECHCOMBANK', 'name': 'Techcombank', 'type': 'atm'},
            {'code': 'MBBANK', 'name': 'MB Bank', 'type': 'atm'},
            {'code': 'ACB', 'name': 'ACB', 'type': 'atm'},
            {'code': 'OCB', 'name': 'OCB', 'type': 'atm'},
            {'code': 'IVB', 'name': 'IndovinaBank', 'type': 'atm'},
            {'code': 'VISA', 'name': 'Visa/Master', 'type': 'intcard'},
            {'code': 'VNPAYQR', 'name': 'VNPAYQR', 'type': 'qrcode'},
        ]


# Factory function
def create_vnpay_gateway(merchant_id: str = None, secret_key: str = None,
                        is_sandbox: bool = True) -> VNPayGateway:
    """🏭 Factory để tạo VNPay gateway instance"""

    # Default sandbox credentials (for testing)
    if merchant_id is None:
        merchant_id = "FADO001"  # Replace with actual merchant ID

    if secret_key is None:
        secret_key = "FADOSECRETKEY123456789"  # Replace with actual secret key

    return VNPayGateway(merchant_id, secret_key, is_sandbox)


# Test function
async def test_vnpay_integration():
    """🧪 Test VNPay integration"""

    gateway = create_vnpay_gateway()

    # Test payment creation
    order_data = {
        'order_id': 12345,
        'amount': 500000,  # 500,000 VND
        'description': 'Test order payment',
        'customer': {
            'phone': '0123456789',
            'email': 'test@fado.vn',
            'full_name': 'Nguyen Van Test',
            'address': 'Ha Noi, Vietnam'
        }
    }

    return_url = "https://fado.vn/payment/return"
    ipn_url = "https://fado.vn/payment/webhook"

    result = gateway.create_payment_url(order_data, return_url, ipn_url)

    if result['success']:
        print("✅ VNPay payment URL created successfully")
        print(f"Payment URL: {result['payment_url']}")
        print(f"Transaction Ref: {result['transaction_ref']}")
    else:
        print(f"❌ Failed to create payment URL: {result['error']}")

    return result