# 📝 FADO CRM - Logging Configuration Siêu Đỉnh!
# Logging như một detective theo dõi mọi hoạt động! 🕵️

import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime

# 📁 Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# 🎯 Remove default loguru handler
logger.remove()

# 📺 Console logging (for development) - No emojis for Windows console
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<level>{message}</level>",
    level="INFO",
    colorize=True,
    backtrace=True,
    diagnose=True,
    filter=lambda record: not any(emoji in record["message"] for emoji in ["🚀", "✅", "🎉", "😞", "🔍", "📝", "📈"])
)

# 📁 File logging (for production)
logger.add(
    LOGS_DIR / "fado_crm_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    encoding="utf-8"
)

# 🚨 Error file logging
logger.add(
    LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message} | {extra}",
    level="ERROR",
    rotation="1 day",
    retention="30 days",
    compression="zip",
    encoding="utf-8"
)

# 📊 Access logging
access_logger = logger.bind(logger_type="access")
logger.add(
    LOGS_DIR / "access_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | ACCESS | {message}",
    level="INFO",
    rotation="1 day",
    retention="7 days",
    filter=lambda record: record["extra"].get("logger_type") == "access"
)

# 💾 Database logging
db_logger = logger.bind(logger_type="database")
logger.add(
    LOGS_DIR / "database_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | DATABASE | {level: <8} | {message}",
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    filter=lambda record: record["extra"].get("logger_type") == "database"
)

# 🎯 Custom logging functions
def log_api_call(method: str, path: str, status_code: int, duration: float, user_id: str = None):
    """📞 Log API call"""
    access_logger.info(
        f"{method} {path} - {status_code} - {duration:.3f}s" +
        (f" - User: {user_id}" if user_id else "")
    )

def log_database_query(query: str, duration: float, rows_affected: int = None):
    """💾 Log database query"""
    db_logger.debug(
        f"Query executed in {duration:.3f}s" +
        (f" - {rows_affected} rows affected" if rows_affected is not None else ""),
        extra={"query": query}
    )

def log_error_with_context(error: Exception, context: dict = None):
    """🚨 Log error với context"""
    logger.error(
        f"Error occurred: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "context": context or {},
            "traceback": logger.opt(exception=True).info("Exception details")
        }
    )

def log_user_action(user_id: str, action: str, resource: str, resource_id: str = None):
    """👤 Log user action"""
    logger.info(
        f"User {user_id} performed {action} on {resource}" +
        (f" (ID: {resource_id})" if resource_id else ""),
        extra={
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id
        }
    )

def log_business_event(event_type: str, details: dict):
    """📈 Log business event"""
    logger.info(
        f"Business event: {event_type}",
        extra={
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# 🎉 Export logger
app_logger = logger

# 🎯 Helper để bind context
def get_logger_with_context(**context):
    """📝 Get logger với context"""
    return logger.bind(**context)

# 🚀 Logging system ready! Giờ có thể track mọi thứ như NSA! 🕵️‍♂️