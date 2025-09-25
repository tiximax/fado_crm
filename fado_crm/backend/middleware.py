# 🛡️ FADO CRM - Middleware Siêu Bảo Vệ!
# Middleware như lá chắn bảo vệ API khỏi mọi tấn công! ⚔️

import time
import uuid
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from exceptions import (
    FADOException,
    format_error_response,
    format_http_exception,
    format_validation_error
)
from logging_config import app_logger, log_api_call, log_error_with_context

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """🚨 Global error handler middleware"""

    async def dispatch(self, request: Request, call_next):
        # 🆔 Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # ⏱️ Start timing
        start_time = time.time()

        try:
            # 📞 Process request
            response = await call_next(request)

            # ⏱️ Calculate duration
            duration = time.time() - start_time

            # 📝 Log successful API call
            log_api_call(
                method=request.method,
                path=str(request.url.path),
                status_code=response.status_code,
                duration=duration
            )

            # 🆔 Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except FADOException as e:
            # 🎯 Handle custom FADO exceptions
            duration = time.time() - start_time

            app_logger.warning(
                f"FADO Exception: {e.error_code} - {e.message}",
                extra={
                    "request_id": request_id,
                    "path": str(request.url.path),
                    "method": request.method,
                    "error_code": e.error_code,
                    "details": e.details
                }
            )

            log_api_call(
                method=request.method,
                path=str(request.url.path),
                status_code=e.status_code,
                duration=duration
            )

            return JSONResponse(
                status_code=e.status_code,
                content=format_error_response(e),
                headers={"X-Request-ID": request_id}
            )

        except HTTPException as e:
            # 🌐 Handle FastAPI HTTP exceptions
            duration = time.time() - start_time

            app_logger.warning(
                f"HTTP Exception: {e.status_code} - {e.detail}",
                extra={
                    "request_id": request_id,
                    "path": str(request.url.path),
                    "method": request.method,
                    "status_code": e.status_code
                }
            )

            log_api_call(
                method=request.method,
                path=str(request.url.path),
                status_code=e.status_code,
                duration=duration
            )

            return JSONResponse(
                status_code=e.status_code,
                content=format_http_exception(e),
                headers={"X-Request-ID": request_id}
            )

        except ValidationError as e:
            # 📋 Handle Pydantic validation errors
            duration = time.time() - start_time

            app_logger.warning(
                f"Validation Error: {str(e)}",
                extra={
                    "request_id": request_id,
                    "path": str(request.url.path),
                    "method": request.method,
                    "validation_errors": e.errors()
                }
            )

            log_api_call(
                method=request.method,
                path=str(request.url.path),
                status_code=422,
                duration=duration
            )

            return JSONResponse(
                status_code=422,
                content=format_validation_error(e.errors()),
                headers={"X-Request-ID": request_id}
            )

        except Exception as e:
            # 🚨 Handle unexpected errors
            duration = time.time() - start_time

            log_error_with_context(
                error=e,
                context={
                    "request_id": request_id,
                    "path": str(request.url.path),
                    "method": request.method,
                    "query_params": dict(request.query_params),
                    "headers": dict(request.headers)
                }
            )

            log_api_call(
                method=request.method,
                path=str(request.url.path),
                status_code=500,
                duration=duration
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "Đã xảy ra lỗi không mong muốn",
                    "request_id": request_id,
                    "timestamp": time.time()
                },
                headers={"X-Request-ID": request_id}
            )

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """📝 Request logging middleware"""

    async def dispatch(self, request: Request, call_next):
        # 📊 Log incoming request
        app_logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "query_params": dict(request.query_params),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None
            }
        )

        response = await call_next(request)
        return response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """🔒 Security headers middleware"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # 🛡️ Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response

# 🚀 Middleware stack hoàn thành! Giờ API an toàn như Fort Knox! 🏰