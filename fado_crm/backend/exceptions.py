# 🚨 FADO CRM - Custom Exceptions & Error Handlers
# Xử lý lỗi như một ninja bảo vệ ứng dụng! 🥷

from fastapi import HTTPException
from typing import Any, Dict, Optional
import traceback
from datetime import datetime

class FADOException(Exception):
    """🎯 Base exception class cho FADO CRM"""

    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)

class ValidationError(FADOException):
    """📋 Lỗi validation dữ liệu"""

    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field, **(details or {})}
        )

class NotFoundError(FADOException):
    """🔍 Lỗi không tìm thấy dữ liệu"""

    def __init__(self, resource: str, resource_id: Any = None):
        message = f"Không tìm thấy {resource}"
        if resource_id:
            message += f" với ID: {resource_id}"

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id}
        )

class ConflictError(FADOException):
    """⚔️ Lỗi conflict dữ liệu"""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            status_code=409,
            details=details
        )

class DatabaseError(FADOException):
    """🗄️ Lỗi database"""

    def __init__(self, message: str = "Lỗi cơ sở dữ liệu", details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details
        )

class AuthenticationError(FADOException):
    """🔐 Lỗi xác thực"""

    def __init__(self, message: str = "Xác thực thất bại"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )

class AuthorizationError(FADOException):
    """🚫 Lỗi phân quyền"""

    def __init__(self, message: str = "Không có quyền truy cập"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403
        )

class RateLimitError(FADOException):
    """⏱️ Lỗi rate limiting"""

    def __init__(self, message: str = "Quá nhiều yêu cầu"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=429
        )

# 📊 Error response format
def format_error_response(exception: FADOException) -> Dict[str, Any]:
    """🎨 Format error response cho API"""

    return {
        "error": True,
        "error_code": exception.error_code,
        "message": exception.message,
        "timestamp": exception.timestamp.isoformat(),
        "details": exception.details
    }

def format_http_exception(exception: HTTPException) -> Dict[str, Any]:
    """🎨 Format standard HTTP exception"""

    return {
        "error": True,
        "error_code": "HTTP_ERROR",
        "message": exception.detail,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": exception.status_code
    }

def format_validation_error(errors: list) -> Dict[str, Any]:
    """🎨 Format pydantic validation error"""

    return {
        "error": True,
        "error_code": "VALIDATION_ERROR",
        "message": "Dữ liệu không hợp lệ",
        "timestamp": datetime.utcnow().isoformat(),
        "details": {
            "validation_errors": [
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                }
                for error in errors
            ]
        }
    }

# 🎯 Success response format
def format_success_response(
    data: Any = None,
    message: str = "Thành công",
    meta: Dict[str, Any] = None
) -> Dict[str, Any]:
    """✅ Format success response"""

    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }

    if data is not None:
        response["data"] = data

    if meta:
        response["meta"] = meta

    return response

# 🚀 Siêu mạnh! Giờ có error handling như Fort Knox! 🛡️