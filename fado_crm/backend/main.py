# 🚀 FADO CRM - FastAPI Backend Siêu Tốc!
# API này nhanh như tia chớp và mạnh như Thor! ⚡

from fastapi import FastAPI, Depends, HTTPException, Query, status, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, or_, desc, asc, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import os

# Import các modules tự tạo - Đây là những đứa con tinh thần của chúng ta! 👨‍👩‍👧‍👦
from database import get_db, create_tables
from models import KhachHang, SanPham, DonHang, ChiTietDonHang, LichSuLienHe, NguoiDung, TrangThaiDonHang, LoaiKhachHang, VaiTro, AuditLog, SystemSetting
import schemas

# 🔐 Import authentication system
from auth import (
    login_user, get_current_user, get_current_active_user,
    get_admin_user, get_manager_user, get_password_hash,
    refresh_access_token
)

# 📊 Import advanced analytics
from analytics_service import get_analytics_data, get_business_insights
# Optional advanced modules (non-blocking)
try:
    from analytics import get_analytics_service
    from ai_recommendations import get_ai_recommendation_engine
    from advanced_export import get_advanced_export_service
    from performance_monitor import get_performance_monitor, PerformanceMiddleware
    OPTIONAL_MODULES_AVAILABLE = True
except Exception:
    OPTIONAL_MODULES_AVAILABLE = False

# 📁 Import file service
from file_service import upload_product_image, upload_multiple_images, delete_product_image, file_service

# 🔍 Import search service
from search_service import universal_search, advanced_search, get_search_suggestions

# 📊 Import export/import service
from export_service import export_service
from services.payment_service import (
    create_transaction, get_order_amount, generate_txn_ref,
    set_txn_gateway_ref, update_status_by_ref
)
from integrations.payment.vnpay import build_payment_url, verify_signature

# 🔔 Import WebSocket service
from websocket_service import manager, notification_service

# 📈 Optional metrics (Prometheus)
try:
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, REGISTRY
    METRICS_AVAILABLE = True
except Exception:
    METRICS_AVAILABLE = False

# ⏱️ Optional rate limiting
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])  # default
    RATE_LIMITING = True
except Exception:
    limiter = None
    RATE_LIMITING = False

# Helper decorator to conditionally apply rate limits
def rate_limit(limit_str: str):
    def decorator(func):
        if RATE_LIMITING and limiter:
            return limiter.limit(limit_str)(func)
        return func
    return decorator

# 💾 Database engine (for health check)
from database import engine

# 🚀 Caching (Redis) optional
try:
    from cache import cache
    CACHE_AVAILABLE = True
except Exception:
    CACHE_AVAILABLE = False

# 🛡️ Import error handling & logging
from exceptions import (
    NotFoundError, ValidationError, ConflictError, DatabaseError,
    format_success_response
)
from logging_config import app_logger, log_user_action, log_business_event
from middleware import ErrorHandlerMiddleware, RequestLoggingMiddleware, SecurityHeadersMiddleware

# 🎪 Khởi tạo FastAPI app với title siêu ngầu!
app = FastAPI(
    title="🛍️ FADO.VN CRM API",
    description="API CRM cho ngành mua hộ - Code bởi AI với tình yêu! 💖",
    version="1.0.0",
    docs_url="/docs",  # 📚 Swagger UI
    redoc_url="/redoc"  # 📖 ReDoc
)

# 🔍 Add Performance Monitoring Middleware (optional)
try:
    if OPTIONAL_MODULES_AVAILABLE:
        app.add_middleware(PerformanceMiddleware)
except Exception:
    pass

# 🍓 Optional GraphQL endpoint at /graphql
try:
    from strawberry.fastapi import GraphQLRouter
    from graphql_schema import schema as gql_schema
    graphql_app = GraphQLRouter(gql_schema)
    app.include_router(graphql_app, prefix="/graphql")
except Exception:
    app_logger.info("GraphQL not enabled (strawberry not installed or schema import failed)")

# 🛡️ Add security and error handling middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware if available
if RATE_LIMITING:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, lambda r, e: Response(status_code=429, content='{"message":"Rate limit exceeded","success":false}', media_type="application/json"))
    app.add_middleware(SlowAPIMiddleware)

# 🌍 CORS - Cho phép frontend gọi API từ domain khác
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên chỉ định cụ thể domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Static file serving for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 🏗️ Startup event - Tạo database khi khởi động
@app.on_event("startup")
async def startup_event():
    app_logger.info("🚀 Starting FADO CRM API...")
    try:
        create_tables()
        app_logger.success("✅ Database tables created successfully")
        app_logger.info("🎉 FADO CRM API is ready to serve!")

        # 📊 Log business event
        log_business_event("API_STARTUP", {
            "version": "1.0.0",
            "environment": "development"
        })

    except Exception as e:
        app_logger.error(f"❌ Failed to start API: {str(e)}")
        raise

# 🏠 Root endpoint - Chào mừng đến với API!
@app.get("/", response_model=schemas.MessageResponse)
async def root():
    """Endpoint chao mung - Hello World phien ban sieu xin!"""
    return schemas.MessageResponse(
        message="Chao mung den voi FADO.VN CRM API! San sang phuc vu!",
        success=True
    )

# ❤️ Health check endpoint
@app.get("/health")
async def health_check():
    # Database health
    db_ok = False
    db_error = None
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        db_error = str(e)

    # Cache health
    cache_status = {"enabled": CACHE_AVAILABLE}
    if CACHE_AVAILABLE:
        try:
            info = cache.health()
            cache_status.update({"status": "ok", **info})
        except Exception as e:
            cache_status.update({"status": "error", "error": str(e)})
    else:
        cache_status.update({"status": "disabled"})

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else {"status": "error", "error": db_error},
        "cache": cache_status,
        "version": "1.0.0"
    }

# 💳 PAYMENTS ENDPOINTS (VNPay)
@app.post("/payments/create", response_model=schemas.PaymentCreateResponse)
async def create_payment(payload: schemas.PaymentCreateRequest, current_user: NguoiDung = Depends(get_current_active_user), db: Session = Depends(get_db)):
    order_id = payload.order_id
    amount = get_order_amount(db, order_id)
    if amount is None or amount <= 0:
        raise HTTPException(status_code=400, detail="Đơn hàng không hợp lệ hoặc số tiền = 0")

    txn = create_transaction(db, order_id, amount, method="vnpay")
    txn_ref = generate_txn_ref()
    set_txn_gateway_ref(db, txn.transaction_id, txn_ref)

    # Build VNPay redirect URL
    tmn_code = os.getenv("VNPAY_TMN_CODE", "demo")
    return_url = os.getenv("VNPAY_RETURN_URL", "http://127.0.0.1:8000/payments/return")
    pay_url = os.getenv("VNPAY_PAYMENT_URL", "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html")
    secret = os.getenv("VNPAY_HASH_SECRET", "secret")

    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": tmn_code,
        "vnp_Amount": int(amount * 100),  # VND x100
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": txn_ref,
        "vnp_OrderInfo": f"FADO Order {order_id}",
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_ReturnUrl": return_url,
        "vnp_CreateDate": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": "127.0.0.1",
    }
    redirect_url = build_payment_url(params, secret, pay_url)

    return schemas.PaymentCreateResponse(
        transaction_id=txn.transaction_id,
        txn_ref=txn_ref,
        redirect_url=redirect_url
    )

@app.get("/payments/return")
async def vnpay_return(request: Request, db: Session = Depends(get_db)):
    q = dict(request.query_params)
    secret = os.getenv("VNPAY_HASH_SECRET", "secret")
    if not verify_signature(q, secret):
        raise HTTPException(status_code=400, detail="Chữ ký không hợp lệ")

    txn_ref = q.get("vnp_TxnRef")
    resp_code = q.get("vnp_ResponseCode")
    status = PaymentStatus.SUCCESS if resp_code == "00" else PaymentStatus.FAILED
    update_status_by_ref(db, txn_ref, status)

    return {"success": True, "message": "Payment processed", "txn_ref": txn_ref, "status": status.value}

@app.post("/payments/webhook")
async def vnpay_webhook(payload: Dict[str, Any], request: Request, db: Session = Depends(get_db)):
    # VNPay may send form or json; handle both
    data = payload or {}
    if not data and request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
        body = await request.body()
        s = body.decode("utf-8")
        pairs = [kv.split("=") for kv in s.split("&") if "=" in kv]
        data = {k: v for k, v in pairs}

    secret = os.getenv("VNPAY_HASH_SECRET", "secret")
    if not verify_signature(data, secret):
        raise HTTPException(status_code=400, detail="Chữ ký không hợp lệ")

    txn_ref = data.get("vnp_TxnRef")
    resp_code = data.get("vnp_ResponseCode")
    status = PaymentStatus.SUCCESS if resp_code == "00" else PaymentStatus.FAILED
    update_status_by_ref(db, txn_ref, status)

    return {"RspCode": "00", "Message": "Confirm Success"}

# 📊 Prometheus metrics (if available)
if METRICS_AVAILABLE:
    @app.get("/metrics")
    async def metrics():
        data = generate_latest(REGISTRY)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# 📝 Admin: Audit logs
@app.get("/admin/audit-logs", response_model=List[schemas.AuditLog])
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

# ⚙️ Admin: System Settings
@app.get("/admin/system-settings", response_model=List[schemas.SystemSetting])
async def list_settings(
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    settings = db.query(SystemSetting).order_by(SystemSetting.key.asc()).all()
    return settings

@app.get("/admin/system-settings/{key}", response_model=schemas.SystemSetting)
async def get_setting(
    key: str,
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Không tìm thấy cấu hình")
    return setting

@app.put("/admin/system-settings/{key}", response_model=schemas.SystemSetting)
async def upsert_setting(
    key: str,
    payload: schemas.SystemSettingUpdate,
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
    if not setting:
        setting = SystemSetting(key=key, value=payload.value, description=payload.description)
        db.add(setting)
    else:
        setting.value = payload.value
        if payload.description is not None:
            setting.description = payload.description
        setting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(setting)
    return setting

# 🧹 Cache control endpoints (Admin only)
@app.post("/cache/flush", response_model=schemas.MessageResponse)
async def flush_cache(admin_user: NguoiDung = Depends(get_admin_user)):
    if not CACHE_AVAILABLE:
        return schemas.MessageResponse(message="Cache is disabled", success=False)
    try:
        cache.flush()
        return schemas.MessageResponse(message="Đã xóa cache thành công", success=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flush cache failed: {str(e)}")

# 🌐 Public settings (read-only)
@app.get("/settings/public")
async def get_public_settings(db: Session = Depends(get_db)):
    """Trả về các cấu hình công khai cho frontend (không cần xác thực)."""
    public_keys = ["app_name"]
    result: Dict[str, Any] = {}

    for key in public_keys:
        setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        if setting:
            result[key] = setting.value

    # Giá trị mặc định nếu chưa có trong DB
    result.setdefault("app_name", "FADO.VN CRM")
    return result

# 🔐 AUTHENTICATION ENDPOINTS - Hệ thống xác thực siêu bảo mật!

@rate_limit("10/minute")
@app.post("/auth/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db), request: Request = None):
    """🎪 Đăng nhập và lấy JWT token"""
    try:
        # Per-IP login burst protection (10 attempts per 60s)
        try:
            if CACHE_AVAILABLE and request is not None:
                ip = request.client.host if request.client else "unknown"
                rl_key = f"rl:login:{ip}"
                attempts = cache.incr(rl_key, ex=60)
                if attempts > 10:
                    raise HTTPException(status_code=429, detail="Quá nhiều lần đăng nhập. Vui lòng thử lại sau 1 phút.")
        except Exception:
            # Fail-open if cache not available
            pass

        result = login_user(db, login_data.email, login_data.password)

        # Record audit log
        try:
            user_id = result["user"]["id"] if isinstance(result, dict) and "user" in result else None
            ip = request.client.host if request and request.client else None
            ua = request.headers.get("user-agent") if request else None
            audit = AuditLog(
                action="login",
                resource="auth",
                resource_id="login",
                user_id=user_id,
                ip_address=ip,
                user_agent=ua,
                details=None
            )
            db.add(audit)
            db.commit()
        except Exception:
            db.rollback()

        log_user_action(
            user_id=str(result["user"]["id"]),
            action="login",
            resource="auth",
            resource_id="login"
        )
        return schemas.LoginResponse(**result)
    except Exception as e:
        app_logger.error(f"Login failed for {login_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )


@app.post("/auth/refresh", response_model=schemas.TokenResponse)
async def refresh_token(refresh_data: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    """🔄 Refresh JWT access token"""
    try:
        result = refresh_access_token(refresh_data.refresh_token, db)
        return schemas.TokenResponse(**result)
    except Exception as e:
        app_logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ"
        )

@app.get("/auth/me", response_model=schemas.NguoiDung)
async def get_current_user_info(current_user: NguoiDung = Depends(get_current_active_user)):
    """👤 Lấy thông tin người dùng hiện tại"""
    return current_user

@app.post("/auth/change-password", response_model=schemas.MessageResponse)
async def change_password(
    password_data: schemas.ChangePasswordRequest,
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🔐 Đổi mật khẩu"""
    from auth import verify_password, get_password_hash

    # Verify old password
    if not verify_password(password_data.old_password, current_user.mat_khau_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu cũ không chính xác"
        )

    # Update password
    current_user.mat_khau_hash = get_password_hash(password_data.new_password)
    db.commit()

    log_user_action(
        user_id=str(current_user.id),
        action="change_password",
        resource="auth",
        resource_id=str(current_user.id)
    )

    return schemas.MessageResponse(
        message="🔐 Đổi mật khẩu thành công!",
        success=True
    )

# 👤 USER MANAGEMENT ENDPOINTS - Quản lý người dùng siêu pro!

@app.get("/users/", response_model=List[schemas.NguoiDung])
async def get_users_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """👥 Lấy danh sách người dùng (Admin only)"""
    users = db.query(NguoiDung).offset(skip).limit(limit).all()
    return users

@app.post("/users/", response_model=schemas.NguoiDung)
async def create_user(
    user_data: schemas.NguoiDungCreate,
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """🆕 Tạo người dùng mới (Admin only)"""

    # Check if email already exists
    existing_user = db.query(NguoiDung).filter(NguoiDung.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="📧 Email này đã được sử dụng!"
        )

    # Create new user
    user_dict = user_data.dict()
    password = user_dict.pop("password")
    user_dict["mat_khau_hash"] = get_password_hash(password)

    new_user = NguoiDung(**user_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_user_action(
        user_id=str(admin_user.id),
        action="create",
        resource="user",
        resource_id=str(new_user.id)
    )

    return new_user

@app.put("/users/{user_id}", response_model=schemas.NguoiDung)
async def update_user(
    user_id: int,
    user_update: schemas.NguoiDungUpdate,
    manager_user: NguoiDung = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """🔄 Cập nhật người dùng (Manager/Admin only)"""

    user = db.query(NguoiDung).filter(NguoiDung.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="👤 Không tìm thấy người dùng!"
        )

    # Update user fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    log_user_action(
        user_id=str(manager_user.id),
        action="update",
        resource="user",
        resource_id=str(user_id)
    )

    return user

# 📊 Dashboard/Thống kê tổng quan
@app.get("/dashboard", response_model=schemas.ThongKeResponse)
async def get_dashboard(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Dashboard siêu cool với thống kê realtime!"""

    # 🗓️ Thời gian cho thống kê tháng này
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    # 📈 Tính toán các chỉ số như một data scientist!
    tong_khach_hang = db.query(KhachHang).count()
    tong_don_hang = db.query(DonHang).count()

    # 💰 Doanh thu tháng này
    doanh_thu_thang = db.query(func.sum(DonHang.tong_tien)).filter(
        DonHang.ngay_tao >= start_of_month,
        DonHang.trang_thai != TrangThaiDonHang.HUY
    ).scalar() or 0.0

    # ⏳ Đơn chờ xử lý
    don_cho_xu_ly = db.query(DonHang).filter(
        DonHang.trang_thai.in_([
            TrangThaiDonHang.CHO_XAC_NHAN,
            TrangThaiDonHang.DA_XAC_NHAN,
            TrangThaiDonHang.DANG_MUA
        ])
    ).count()

    # 🆕 Khách mới tháng này
    khach_moi_thang = db.query(KhachHang).filter(
        KhachHang.ngay_tao >= start_of_month
    ).count()

    return schemas.ThongKeResponse(
        tong_khach_hang=tong_khach_hang,
        tong_don_hang=tong_don_hang,
        doanh_thu_thang=doanh_thu_thang,
        don_cho_xu_ly=don_cho_xu_ly,
        khach_moi_thang=khach_moi_thang
    )

# 📊 ADVANCED ANALYTICS ENDPOINTS - Business Intelligence siêu đỉnh!

@app.get("/analytics/dashboard")
async def get_advanced_dashboard(
    date_range: int = Query(30, ge=1, le=365, description="📅 Số ngày phân tích"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Dashboard analytics nâng cao với charts và insights"""
    try:
        log_user_action(
            user_id=str(current_user.id),
            action="view",
            resource="analytics",
            resource_id="dashboard"
        )

        analytics_data = get_analytics_data(db, date_range)

        # Log business event
        log_business_event("ANALYTICS_VIEWED", {
            "user_id": current_user.id,
            "user_role": current_user.vai_tro.value,
            "date_range": date_range
        })

        return {
            "success": True,
            "data": analytics_data,
            "message": f"📊 Analytics data for {date_range} days"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting advanced analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy dữ liệu analytics"
        )

@app.get("/analytics/insights")
async def get_ai_insights(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🧠 AI-powered business insights và recommendations"""
    try:
        # Require manager or admin for insights
        if current_user.vai_tro not in [VaiTro.ADMIN, VaiTro.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cần quyền Manager hoặc Admin để xem insights"
            )

        insights_data = get_business_insights(db)

        log_user_action(
            user_id=str(current_user.id),
            action="view",
            resource="analytics",
            resource_id="insights"
        )

        return {
            "success": True,
            "data": insights_data,
            "message": "🧠 AI Business Insights generated successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error getting business insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tạo business insights"
        )

@app.get("/analytics/revenue-trend")
async def get_revenue_trend(
    days: int = Query(30, ge=7, le=365, description="📅 Số ngày"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📈 Chi tiết xu hướng doanh thu theo ngày"""
    try:
        from analytics_service import analytics_service
        analytics_service.set_session(db)

        trend_data = analytics_service.get_daily_revenue_trend(days)

        return {
            "success": True,
            "data": trend_data,
            "message": f"📈 Revenue trend for {days} days"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting revenue trend: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy xu hướng doanh thu"
        )

@app.get("/analytics/customers")
async def get_customer_analytics(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """👥 Phân tích chi tiết về khách hàng"""
    try:
        from analytics_service import analytics_service
        analytics_service.set_session(db)

        customer_data = analytics_service.get_customer_analytics()

        return {
            "success": True,
            "data": customer_data,
            "message": "👥 Customer analytics generated"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting customer analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích khách hàng"
        )

@app.get("/analytics/products")
async def get_product_analytics(
    limit: int = Query(20, ge=5, le=100, description="🔢 Số lượng sản phẩm top"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🛍️ Phân tích hiệu suất sản phẩm"""
    try:
        from analytics_service import analytics_service
        analytics_service.set_session(db)

        product_data = analytics_service.get_product_performance(limit)

        return {
            "success": True,
            "data": product_data,
            "message": f"🛍️ Top {limit} product performance data"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting product analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích sản phẩm"
        )

# 📁 FILE UPLOAD ENDPOINTS - Quản lý file như Google Drive!

@app.post("/upload/product-image")
async def upload_product_image_endpoint(
    file: UploadFile = File(..., description="🖼️ Hình ảnh sản phẩm"),
    product_id: Optional[int] = Form(None, description="🔢 ID sản phẩm (optional)"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📸 Upload hình ảnh cho sản phẩm"""
    try:
        # Check permission (Staff+ can upload)
        if current_user.vai_tro not in [VaiTro.ADMIN, VaiTro.MANAGER, VaiTro.STAFF]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cần quyền Staff trở lên để upload hình ảnh"
            )

        # Validate product exists if product_id provided
        if product_id:
            product = db.query(SanPham).filter(SanPham.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy sản phẩm"
                )

        # Upload image
        result = await upload_product_image(file, current_user, product_id)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="upload",
            resource="product_image",
            resource_id=str(product_id) if product_id else "new"
        )

        # Log business event
        log_business_event("IMAGE_UPLOADED", {
            "user_id": current_user.id,
            "filename": result["file_info"]["stored_filename"],
            "product_id": product_id,
            "file_size": result["file_info"]["file_size"]
        })

        return {
            "success": True,
            "message": "📸 Upload hình ảnh thành công!",
            "data": result
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error uploading product image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi upload hình ảnh"
        )

@app.post("/upload/multiple-images")
async def upload_multiple_images_endpoint(
    files: List[UploadFile] = File(..., description="🖼️ Nhiều hình ảnh sản phẩm"),
    product_id: Optional[int] = Form(None, description="🔢 ID sản phẩm (optional)"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📁 Upload nhiều hình ảnh cùng lúc"""
    try:
        # Check permission
        if current_user.vai_tro not in [VaiTro.ADMIN, VaiTro.MANAGER, VaiTro.STAFF]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cần quyền Staff trở lên để upload hình ảnh"
            )

        # Limit number of files
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tối đa 10 file mỗi lần upload"
            )

        # Validate product if provided
        if product_id:
            product = db.query(SanPham).filter(SanPham.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Không tìm thấy sản phẩm"
                )

        # Upload all images
        results = await upload_multiple_images(files, current_user, product_id)

        # Count successes
        successful_uploads = sum(1 for result in results if result.get("success", False))
        failed_uploads = len(results) - successful_uploads

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="bulk_upload",
            resource="product_images",
            resource_id=str(product_id) if product_id else "multiple"
        )

        return {
            "success": True,
            "message": f"📁 Upload hoàn thành: {successful_uploads} thành công, {failed_uploads} thất bại",
            "data": {
                "total_files": len(files),
                "successful": successful_uploads,
                "failed": failed_uploads,
                "results": results
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error uploading multiple images: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi upload nhiều hình ảnh"
        )

@app.delete("/upload/image/{filename}")
async def delete_image_endpoint(
    filename: str,
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🗑️ Xóa hình ảnh sản phẩm"""
    try:
        # Check permission (Manager+ can delete)
        if current_user.vai_tro not in [VaiTro.ADMIN, VaiTro.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cần quyền Manager trở lên để xóa hình ảnh"
            )

        # Get file info first
        file_info = file_service.get_file_info(filename, "image")
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy file hình ảnh"
            )

        # Delete file
        success = delete_product_image(filename)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Lỗi khi xóa file"
            )

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="delete",
            resource="product_image",
            resource_id=filename
        )

        return {
            "success": True,
            "message": f"🗑️ Đã xóa hình ảnh: {filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error deleting image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xóa hình ảnh"
        )

@app.get("/upload/storage-stats")
async def get_storage_stats(
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """📊 Thống kê storage (Admin only)"""
    try:
        stats = file_service.get_storage_stats()

        return {
            "success": True,
            "data": stats,
            "message": "📊 Storage statistics retrieved"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting storage stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy thống kê storage"
        )

@app.post("/upload/cleanup-temp")
async def cleanup_temp_files(
    older_than_hours: int = Query(24, ge=1, le=168, description="⏰ Xóa file cũ hơn (giờ)"),
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """🧹 Dọn dẹp file tạm (Admin only)"""
    try:
        deleted_count = file_service.cleanup_temp_files(older_than_hours)

        return {
            "success": True,
            "message": f"🧹 Đã xóa {deleted_count} file tạm",
            "data": {
                "deleted_files": deleted_count,
                "older_than_hours": older_than_hours
            }
        }

    except Exception as e:
        app_logger.error(f"❌ Error cleaning up temp files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi dọn dẹp file tạm"
        )

@app.get("/upload/list")
async def list_uploaded_files(
    category: str = Query(..., description="Danh mục: product_images | thumbnails | documents"),
    limit: int = Query(50, ge=1, le=1000),
    current_user: NguoiDung = Depends(get_current_active_user),
    request: Request = None
):
    """📃 Liệt kê file đã upload trong 1 category, trả về URL tuyệt đối"""
    try:
        items = file_service.list_files(category, limit=limit)
        base = str(request.base_url).rstrip('/') if request else ''
        driver = os.getenv('STORAGE_DRIVER', 'local').lower()
        for it in items:
            url = it.get("url", "")
            if driver == 'local' and url.startswith('/'):
                it["url"] = f"{base}{url}"
        return {
            "success": True,
            "category": category,
            "total": len(items),
            "items": items
        }
    except Exception as e:
        app_logger.error(f"❌ Error listing uploaded files: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi khi liệt kê file đã upload")

@app.delete("/upload/file")
async def delete_uploaded_file(
    category: str = Query(..., description="Danh mục: product_images | thumbnails | documents"),
    filename: str = Query(..., description="Tên file cần xóa"),
    manager_user: NguoiDung = Depends(get_manager_user),
):
    """🗑️ Xóa file đã upload. Nếu là ảnh sản phẩm, xóa kèm all thumbnails"""
    try:
        if category == "product_images":
            ok = file_service.delete_file(filename, "image")
        elif category in ("thumbnails", "documents"):
            ok = file_service.storage.delete(category, filename)
        else:
            raise HTTPException(status_code=400, detail="Category không hợp lệ")

        if not ok:
            raise HTTPException(status_code=500, detail="Xóa file thất bại")

        # Log activity
        log_user_action(
            user_id=str(manager_user.id),
            action="delete",
            resource=category,
            resource_id=filename
        )

        return {"success": True, "message": f"Đã xóa {filename} khỏi {category}"}
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error deleting uploaded file: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi khi xóa file")

# 🔍 ADVANCED SEARCH ENDPOINTS - Tìm kiếm như Google!

@app.get("/search")
async def universal_search_endpoint(
    q: str = Query(..., min_length=2, description="🔍 Từ khóa tìm kiếm"),
    limit: int = Query(50, ge=1, le=100, description="🔢 Giới hạn kết quả"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🌍 Universal search across all entities"""
    try:
        results = universal_search(db, q, limit)

        log_user_action(
            user_id=str(current_user.id),
            action="search",
            resource="universal",
            resource_id=q
        )

        return {
            "success": True,
            "query": q,
            "data": results,
            "message": f"🔍 Tìm thấy {results['total']} kết quả cho '{q}'"
        }

    except Exception as e:
        app_logger.error(f"❌ Error in universal search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tìm kiếm"
        )

@app.get("/search/suggestions")
async def get_search_suggestions_endpoint(
    q: str = Query(..., min_length=1, description="🔍 Từ khóa gợi ý"),
    category: str = Query("all", description="📂 Danh mục (all, customers, products, orders)"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """💡 Get search suggestions"""
    try:
        suggestions = get_search_suggestions(db, q, category)

        return {
            "success": True,
            "query": q,
            "suggestions": suggestions
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting search suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy gợi ý tìm kiếm"
        )

@app.post("/search/advanced/customers")
async def advanced_customer_search(
    filters: Dict[str, Any],
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """👥 Advanced customer search with filters"""
    try:
        customers = advanced_search(db, "customers", filters)

        # Convert to response format
        results = []
        for customer in customers:
            results.append({
                "id": customer.id,
                "ho_ten": customer.ho_ten,
                "email": customer.email,
                "so_dien_thoai": customer.so_dien_thoai,
                "loai_khach": customer.loai_khach.value,
                "tong_tien_da_mua": customer.tong_tien_da_mua,
                "so_don_thanh_cong": customer.so_don_thanh_cong,
                "ngay_tao": customer.ngay_tao.isoformat() if customer.ngay_tao else None
            })

        return {
            "success": True,
            "data": results,
            "total": len(results),
            "filters": filters
        }

    except Exception as e:
        app_logger.error(f"❌ Error in advanced customer search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tìm kiếm khách hàng nâng cao"
        )

@app.post("/search/advanced/products")
async def advanced_product_search(
    filters: Dict[str, Any],
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🛍️ Advanced product search with filters"""
    try:
        products = advanced_search(db, "products", filters)

        # Convert to response format
        results = []
        for product in products:
            results.append({
                "id": product.id,
                "ten_san_pham": product.ten_san_pham,
                "danh_muc": product.danh_muc,
                "quoc_gia_nguon": product.quoc_gia_nguon,
                "gia_ban": product.gia_ban,
                "gia_goc": product.gia_goc,
                "trong_luong": product.trong_luong,
                "ngay_tao": product.ngay_tao.isoformat() if product.ngay_tao else None
            })

        return {
            "success": True,
            "data": results,
            "total": len(results),
            "filters": filters
        }

    except Exception as e:
        app_logger.error(f"❌ Error in advanced product search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tìm kiếm sản phẩm nâng cao"
        )

@app.post("/search/advanced/orders")
async def advanced_order_search(
    filters: Dict[str, Any],
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📋 Advanced order search with filters"""
    try:
        orders = advanced_search(db, "orders", filters)

        # Convert to response format
        results = []
        for order in orders:
            results.append({
                "id": order.id,
                "ma_don_hang": order.ma_don_hang,
                "khach_hang": {
                    "id": order.khach_hang.id if order.khach_hang else None,
                    "ho_ten": order.khach_hang.ho_ten if order.khach_hang else None,
                    "email": order.khach_hang.email if order.khach_hang else None
                },
                "trang_thai": order.trang_thai.value,
                "tong_tien": order.tong_tien,
                "ngay_tao": order.ngay_tao.isoformat() if order.ngay_tao else None,
                "ngay_giao_hang": order.ngay_giao_hang.isoformat() if order.ngay_giao_hang else None,
                "ma_van_don": order.ma_van_don
            })

        return {
            "success": True,
            "data": results,
            "total": len(results),
            "filters": filters
        }

    except Exception as e:
        app_logger.error(f"❌ Error in advanced order search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tìm kiếm đơn hàng nâng cao"
        )

# 👥 KHÁCH HÀNG ENDPOINTS - Quản lý customer như một pro!

@app.get("/khach-hang/", response_model=List[schemas.KhachHang])
async def get_khach_hang_list(
    skip: int = Query(0, ge=0, description="📄 Bỏ qua số record"),
    limit: int = Query(100, ge=1, le=1000, description="🔢 Giới hạn số record"),
    search: Optional[str] = Query(None, description="🔍 Tìm kiếm theo tên/email"),
    loai_khach: Optional[LoaiKhachHang] = Query(None, description="🏷️ Lọc theo loại khách"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """👥 Lấy danh sách khách hàng với filter và search siêu mạnh!"""

    query = db.query(KhachHang)

    # 🔍 Search như Google!
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (KhachHang.ho_ten.ilike(search_filter)) |
            (KhachHang.email.ilike(search_filter)) |
            (KhachHang.so_dien_thoai.ilike(search_filter))
        )

    # 🏷️ Filter theo loại khách
    if loai_khach:
        query = query.filter(KhachHang.loai_khach == loai_khach)

    # 📊 Order by ngày tạo mới nhất
    query = query.order_by(KhachHang.ngay_tao.desc())

    return query.offset(skip).limit(limit).all()

@app.get("/khach-hang/{khach_hang_id}", response_model=schemas.KhachHang)
async def get_khach_hang_detail(khach_hang_id: int, db: Session = Depends(get_db)):
    """🔍 Lấy thông tin chi tiết một khách hàng"""

    khach_hang = db.query(KhachHang).filter(KhachHang.id == khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy khách hàng!")

    return khach_hang

@app.post("/khach-hang/", response_model=schemas.KhachHang)
async def create_khach_hang(
    khach_hang: schemas.KhachHangCreate,
    current_user: NguoiDung = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """🆕 Tạo khách hàng mới - Chào mừng thành viên mới!"""

    # 🔍 Kiểm tra email đã tồn tại chưa
    existing_khach = db.query(KhachHang).filter(KhachHang.email == khach_hang.email).first()
    if existing_khach:
        raise HTTPException(status_code=400, detail="📧 Email này đã được sử dụng rồi!")

    # 🎨 Tạo khách hàng mới
    db_khach_hang = KhachHang(**khach_hang.dict())
    db.add(db_khach_hang)
    db.commit()
    db.refresh(db_khach_hang)

    # 🔔 Send WebSocket notification
    try:
        from websocket_service import notify_customer_created
        customer_data = {
            "id": db_khach_hang.id,
            "ho_ten": db_khach_hang.ho_ten,
            "email": db_khach_hang.email,
            "loai_khach": db_khach_hang.loai_khach.value
        }
        await notify_customer_created(customer_data, current_user.id)
    except Exception as e:
        app_logger.error(f"❌ Failed to send notification: {str(e)}")

    return db_khach_hang

@app.put("/khach-hang/{khach_hang_id}", response_model=schemas.KhachHang)
async def update_khach_hang(
    khach_hang_id: int,
    khach_hang_update: schemas.KhachHangUpdate,
    db: Session = Depends(get_db)
):
    """🔄 Cập nhật thông tin khách hàng"""

    khach_hang = db.query(KhachHang).filter(KhachHang.id == khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy khách hàng!")

    # 🔄 Update các field có giá trị
    update_data = khach_hang_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(khach_hang, field, value)

    db.commit()
    db.refresh(khach_hang)
    return khach_hang

# 🛍️ SẢN PHẨM ENDPOINTS - Quản lý hàng hóa như Amazon!

@app.get("/san-pham/", response_model=List[schemas.SanPham])
async def get_san_pham_list(
    skip: int = Query(0, ge=0, description="📄 Bỏ qua số record"),
    limit: int = Query(100, ge=1, le=1000, description="🔢 Giới hạn số record"),
    search: Optional[str] = Query(None, description="🔍 Tìm kiếm sản phẩm"),
    danh_muc: Optional[str] = Query(None, description="📂 Lọc theo danh mục"),
    quoc_gia: Optional[str] = Query(None, description="🌍 Lọc theo quốc gia"),
    gia_min: Optional[float] = Query(None, ge=0, description="💰 Giá tối thiểu"),
    gia_max: Optional[float] = Query(None, ge=0, description="💰 Giá tối đa"),
    sort_by: Optional[str] = Query("ngay_tao", description="📊 Sắp xếp theo (ten_san_pham, gia_ban, ngay_tao)"),
    order: Optional[str] = Query("desc", description="📈 Thứ tự (asc, desc)"),
    db: Session = Depends(get_db)
):
    """🛍️ Lấy danh sách sản phẩm với advanced search và filter"""

    query = db.query(SanPham)

    # 🔍 Advanced search
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                SanPham.ten_san_pham.ilike(search_filter),
                SanPham.mo_ta.ilike(search_filter),
                SanPham.danh_muc.ilike(search_filter)
            )
        )

    # 📂 Filter by category
    if danh_muc:
        query = query.filter(SanPham.danh_muc.ilike(f"%{danh_muc}%"))

    # 🌍 Filter by country
    if quoc_gia:
        query = query.filter(SanPham.quoc_gia_nguon.ilike(f"%{quoc_gia}%"))

    # 💰 Price range filter
    if gia_min is not None:
        query = query.filter(SanPham.gia_ban >= gia_min)
    if gia_max is not None:
        query = query.filter(SanPham.gia_ban <= gia_max)

    # 📊 Dynamic sorting
    sort_column = getattr(SanPham, sort_by, SanPham.ngay_tao)
    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    return query.offset(skip).limit(limit).all()

@app.post("/san-pham/", response_model=schemas.SanPham)
async def create_san_pham(san_pham: schemas.SanPhamCreate, db: Session = Depends(get_db)):
    """🆕 Thêm sản phẩm mới vào kho"""

    try:
        db_san_pham = SanPham(**san_pham.dict())
        db.add(db_san_pham)
        db.commit()
        db.refresh(db_san_pham)

        # 📝 Log user action
        log_user_action(
            user_id="system",
            action="create",
            resource="product",
            resource_id=str(db_san_pham.id)
        )

        # 📈 Log business event
        log_business_event("PRODUCT_CREATED", {
            "product_id": db_san_pham.id,
            "product_name": db_san_pham.ten_san_pham,
            "category": db_san_pham.danh_muc,
            "price": str(db_san_pham.gia)
        })

        return db_san_pham

    except Exception as e:
        db.rollback()
        raise DatabaseError(message="Lỗi khi tạo sản phẩm mới", details={"error": str(e)})

@app.get("/san-pham-count")
async def get_san_pham_count(
    search: Optional[str] = Query(None, description="🔍 Tìm kiếm sản phẩm"),
    danh_muc: Optional[str] = Query(None, description="📂 Lọc theo danh mục"),
    quoc_gia: Optional[str] = Query(None, description="🌍 Lọc theo quốc gia"),
    gia_min: Optional[float] = Query(None, ge=0, description="💰 Giá tối thiểu"),
    gia_max: Optional[float] = Query(None, ge=0, description="💰 Giá tối đa"),
    db: Session = Depends(get_db)
):
    """📊 Đếm số lượng sản phẩm với filter"""

    query = db.query(SanPham)

    # Apply same filters as list endpoint
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                SanPham.ten_san_pham.ilike(search_filter),
                SanPham.mo_ta.ilike(search_filter),
                SanPham.danh_muc.ilike(search_filter)
            )
        )

    if danh_muc:
        query = query.filter(SanPham.danh_muc.ilike(f"%{danh_muc}%"))

    if quoc_gia:
        query = query.filter(SanPham.quoc_gia_nguon.ilike(f"%{quoc_gia}%"))

    if gia_min is not None:
        query = query.filter(SanPham.gia_ban >= gia_min)
    if gia_max is not None:
        query = query.filter(SanPham.gia_ban <= gia_max)

    total = query.count()
    return {"total": total}

@app.get("/san-pham/{san_pham_id}", response_model=schemas.SanPham)
async def get_san_pham_detail(san_pham_id: int, db: Session = Depends(get_db)):
    """🔍 Lấy thông tin chi tiết một sản phẩm"""

    san_pham = db.query(SanPham).filter(SanPham.id == san_pham_id).first()
    if not san_pham:
        raise NotFoundError(resource="sản phẩm", resource_id=san_pham_id)

    # 📝 Log user action
    log_user_action(
        user_id="system",  # Sẽ được thay bằng user thực sau khi có auth
        action="view",
        resource="product",
        resource_id=str(san_pham_id)
    )

    return san_pham

@app.put("/san-pham/{san_pham_id}", response_model=schemas.SanPham)
async def update_san_pham(
    san_pham_id: int,
    san_pham_update: schemas.SanPhamUpdate,
    db: Session = Depends(get_db)
):
    """🔄 Cập nhật thông tin sản phẩm"""

    san_pham = db.query(SanPham).filter(SanPham.id == san_pham_id).first()
    if not san_pham:
        raise NotFoundError(resource="sản phẩm", resource_id=san_pham_id)

    try:
        # 🔄 Update các field có giá trị
        update_data = san_pham_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(san_pham, field, value)

        db.commit()
        db.refresh(san_pham)

        # 📝 Log user action
        log_user_action(
            user_id="system",
            action="update",
            resource="product",
            resource_id=str(san_pham_id)
        )

        return san_pham

    except Exception as e:
        db.rollback()
        raise DatabaseError(message="Lỗi khi cập nhật sản phẩm", details={"error": str(e)})

@app.delete("/san-pham/{san_pham_id}")
async def delete_san_pham(san_pham_id: int, db: Session = Depends(get_db)):
    """🗑️ Xóa sản phẩm (soft delete)"""

    san_pham = db.query(SanPham).filter(SanPham.id == san_pham_id).first()
    if not san_pham:
        raise NotFoundError(resource="sản phẩm", resource_id=san_pham_id)

    try:
        # Soft delete - thêm field is_active vào model sau
        product_name = san_pham.ten_san_pham
        db.delete(san_pham)
        db.commit()

        # 📝 Log user action
        log_user_action(
            user_id="system",
            action="delete",
            resource="product",
            resource_id=str(san_pham_id)
        )

        # 📈 Log business event
        log_business_event("PRODUCT_DELETED", {
            "product_id": san_pham_id,
            "product_name": product_name
        })

        return format_success_response(
            message=f"🗑️ Đã xóa sản phẩm: {product_name}"
        )

    except Exception as e:
        db.rollback()
        raise DatabaseError(message="Lỗi khi xóa sản phẩm", details={"error": str(e)})

# 📋 ĐỢN HÀNG ENDPOINTS - Trái tim của việc mua hộ!

def generate_ma_don_hang() -> str:
    """🎲 Generate mã đơn hàng unique như snowflake!"""
    now = datetime.utcnow()
    timestamp = now.strftime("%y%m%d")
    random_part = str(uuid.uuid4())[:6].upper()
    return f"FD{timestamp}{random_part}"

@app.get("/don-hang/", response_model=List[schemas.DonHang])
async def get_don_hang_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    trang_thai: Optional[TrangThaiDonHang] = Query(None, description="📊 Lọc theo trạng thái"),
    khach_hang_id: Optional[int] = Query(None, description="👤 Lọc theo khách hàng"),
    db: Session = Depends(get_db)
):
    """📋 Lấy danh sách đơn hàng với filter siêu mạnh!"""

    query = db.query(DonHang)

    # 📊 Filter by status
    if trang_thai:
        query = query.filter(DonHang.trang_thai == trang_thai)

    # 👤 Filter by customer
    if khach_hang_id:
        query = query.filter(DonHang.khach_hang_id == khach_hang_id)

    return query.order_by(DonHang.ngay_tao.desc()).offset(skip).limit(limit).all()

@app.get("/don-hang/{don_hang_id}", response_model=schemas.DonHang)
async def get_don_hang_detail(don_hang_id: int, db: Session = Depends(get_db)):
    """📋 Lấy chi tiết đơn hàng với tất cả thông tin"""

    don_hang = db.query(DonHang).filter(DonHang.id == don_hang_id).first()
    if not don_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy đơn hàng!")

    return don_hang

@app.post("/don-hang/", response_model=schemas.DonHang)
async def create_don_hang(don_hang: schemas.DonHangCreate, db: Session = Depends(get_db)):
    """🆕 Tạo đơn hàng mới - Bắt đầu cuộc phiêu lưu mua hộ!"""

    # 🔍 Kiểm tra khách hàng tồn tại
    khach_hang = db.query(KhachHang).filter(KhachHang.id == don_hang.khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy khách hàng!")

    # 🎲 Tạo mã đơn hàng unique
    ma_don_hang = generate_ma_don_hang()
    while db.query(DonHang).filter(DonHang.ma_don_hang == ma_don_hang).first():
        ma_don_hang = generate_ma_don_hang()  # Tạo lại nếu trùng

    # 💰 Tính tổng tiền
    tong_tien = (don_hang.tong_gia_san_pham +
                don_hang.phi_mua_ho +
                don_hang.phi_van_chuyen +
                don_hang.phi_khac)

    # 🎨 Tạo đơn hàng
    db_don_hang = DonHang(
        ma_don_hang=ma_don_hang,
        tong_tien=tong_tien,
        **don_hang.dict(exclude={'chi_tiet_list'})
    )

    db.add(db_don_hang)
    db.commit()
    db.refresh(db_don_hang)

    # 📋 Thêm chi tiết đơn hàng
    for chi_tiet in don_hang.chi_tiet_list:
        # 🔍 Kiểm tra sản phẩm tồn tại
        san_pham = db.query(SanPham).filter(SanPham.id == chi_tiet.san_pham_id).first()
        if not san_pham:
            raise HTTPException(
                status_code=404,
                detail=f"😞 Không tìm thấy sản phẩm ID {chi_tiet.san_pham_id}!"
            )

        db_chi_tiet = ChiTietDonHang(
            don_hang_id=db_don_hang.id,
            **chi_tiet.dict()
        )
        db.add(db_chi_tiet)

    db.commit()
    db.refresh(db_don_hang)

    # 🔔 Send WebSocket notification
    try:
        from websocket_service import notify_order_created
        order_data = {
            "id": db_don_hang.id,
            "ma_don_hang": db_don_hang.ma_don_hang,
            "khach_hang_ten": khach_hang.ho_ten,
            "tong_tien": db_don_hang.tong_tien,
            "trang_thai": db_don_hang.trang_thai.value
        }
        await notify_order_created(order_data, 0)  # System created
    except Exception as e:
        app_logger.error(f"❌ Failed to send order notification: {str(e)}")

    return db_don_hang

@app.put("/don-hang/{don_hang_id}", response_model=schemas.DonHang)
async def update_don_hang(
    don_hang_id: int,
    don_hang_update: schemas.DonHangUpdate,
    db: Session = Depends(get_db)
):
    """🔄 Cập nhật đơn hàng - Theo dõi tiến trình như tracking!"""

    don_hang = db.query(DonHang).filter(DonHang.id == don_hang_id).first()
    if not don_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy đơn hàng!")

    # 🔄 Update fields
    update_data = don_hang_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(don_hang, field, value)

    # 💰 Tính lại tổng tiền nếu có thay đổi phí
    if any(field in update_data for field in ['phi_mua_ho', 'phi_van_chuyen', 'phi_khac']):
        don_hang.tong_tien = (don_hang.tong_gia_san_pham +
                             don_hang.phi_mua_ho +
                             don_hang.phi_van_chuyen +
                             don_hang.phi_khac)

    # ⏰ Cập nhật thời gian
    don_hang.ngay_cap_nhat = datetime.utcnow()

    db.commit()
    db.refresh(don_hang)

    return don_hang

# 📞 LỊCH SỬ LIÊN HỆ ENDPOINTS - CRM không thể thiếu!

@app.get("/lich-su-lien-he/", response_model=List[schemas.LichSuLienHe])
async def get_lich_su_lien_he(
    khach_hang_id: Optional[int] = Query(None, description="👤 ID khách hàng"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """📞 Lấy lịch sử liên hệ với khách hàng"""

    query = db.query(LichSuLienHe)

    if khach_hang_id:
        query = query.filter(LichSuLienHe.khach_hang_id == khach_hang_id)

    return query.order_by(LichSuLienHe.ngay_lien_he.desc()).offset(skip).limit(limit).all()

@app.post("/lich-su-lien-he/", response_model=schemas.LichSuLienHe)
async def create_lich_su_lien_he(
    lich_su: schemas.LichSuLienHeCreate,
    db: Session = Depends(get_db)
):
    """📞 Ghi lại cuộc liên hệ với khách hàng"""

    # 🔍 Kiểm tra khách hàng tồn tại
    khach_hang = db.query(KhachHang).filter(KhachHang.id == lich_su.khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy khách hàng!")

    db_lich_su = LichSuLienHe(**lich_su.dict())
    db.add(db_lich_su)
    db.commit()
    db.refresh(db_lich_su)

    return db_lich_su

# 🎯 Endpoint đặc biệt cho việc cập nhật loại khách hàng tự động
@app.post("/khach-hang/{khach_hang_id}/cap-nhat-loai")
async def auto_update_loai_khach_hang(khach_hang_id: int, db: Session = Depends(get_db)):
    """🤖 Tự động cập nhật loại khách hàng dựa trên lịch sử mua hàng"""

    khach_hang = db.query(KhachHang).filter(KhachHang.id == khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(status_code=404, detail="😞 Không tìm thấy khách hàng!")

    # 📊 Logic phân loại khách hàng tự động
    if khach_hang.tong_tien_da_mua >= 50000000:  # 50 triệu VND
        new_loai = LoaiKhachHang.VIP
    elif khach_hang.tong_tien_da_mua >= 10000000:  # 10 triệu VND
        new_loai = LoaiKhachHang.THAN_THIET
    else:
        new_loai = LoaiKhachHang.MOI

    # 🔄 Cập nhật nếu khác loại hiện tại
    if khach_hang.loai_khach != new_loai:
        khach_hang.loai_khach = new_loai
        db.commit()
        db.refresh(khach_hang)

        return schemas.MessageResponse(
            message=f"🎉 Đã cập nhật loại khách hàng thành {new_loai.value}!",
            success=True
        )

    return schemas.MessageResponse(
        message="ℹ️ Loại khách hàng đã phù hợp, không cần cập nhật.",
        success=True
    )

# 📊 EXPORT/IMPORT ENDPOINTS - Xuất nhập dữ liệu Excel & CSV!

@app.get("/export/customers/excel")
async def export_customers_excel(
    customer_type: Optional[str] = Query(None, description="🏷️ Loại khách hàng"),
    created_from: Optional[datetime] = Query(None, description="📅 Từ ngày"),
    created_to: Optional[datetime] = Query(None, description="📅 Đến ngày"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Export customers to Excel"""
    try:
        from fastapi.responses import Response

        filters = {}
        if customer_type:
            filters["customer_type"] = customer_type
        if created_from:
            filters["created_from"] = created_from
        if created_to:
            filters["created_to"] = created_to

        export_service.set_session(db)
        excel_data = export_service.export_customers_to_excel(filters)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="export",
            resource="customers",
            resource_id="excel"
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"khach_hang_{timestamp}.xlsx"

        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        app_logger.error(f"❌ Error exporting customers to Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất dữ liệu khách hàng"
        )

@app.get("/export/products/excel")
async def export_products_excel(
    category: Optional[str] = Query(None, description="🏷️ Danh mục"),
    country: Optional[str] = Query(None, description="🌍 Quốc gia"),
    min_price: Optional[float] = Query(None, description="💰 Giá tối thiểu"),
    max_price: Optional[float] = Query(None, description="💰 Giá tối đa"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Export products to Excel"""
    try:
        from fastapi.responses import Response

        filters = {}
        if category:
            filters["category"] = category
        if country:
            filters["country"] = country
        if min_price:
            filters["min_price"] = min_price
        if max_price:
            filters["max_price"] = max_price

        export_service.set_session(db)
        excel_data = export_service.export_products_to_excel(filters)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="export",
            resource="products",
            resource_id="excel"
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"san_pham_{timestamp}.xlsx"

        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        app_logger.error(f"❌ Error exporting products to Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất dữ liệu sản phẩm"
        )

@app.get("/export/orders/excel")
async def export_orders_excel(
    status_filter: Optional[List[str]] = Query(None, description="📋 Trạng thái đơn hàng"),
    created_from: Optional[datetime] = Query(None, description="📅 Từ ngày"),
    created_to: Optional[datetime] = Query(None, description="📅 Đến ngày"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Export orders to Excel"""
    try:
        from fastapi.responses import Response

        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if created_from:
            filters["created_from"] = created_from
        if created_to:
            filters["created_to"] = created_to

        export_service.set_session(db)
        excel_data = export_service.export_orders_to_excel(filters)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="export",
            resource="orders",
            resource_id="excel"
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"don_hang_{timestamp}.xlsx"

        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        app_logger.error(f"❌ Error exporting orders to Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất dữ liệu đơn hàng"
        )

@app.get("/export/{entity_type}/csv")
async def export_to_csv(
    entity_type: str,
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📄 Export to CSV format"""
    try:
        from fastapi.responses import Response

        if entity_type not in ["customers", "products", "orders"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid entity type. Must be: customers, products, or orders"
            )

        export_service.set_session(db)
        csv_data = export_service.export_to_csv(entity_type)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="export",
            resource=entity_type,
            resource_id="csv"
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{entity_type}_{timestamp}.csv"

        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        app_logger.error(f"❌ Error exporting to CSV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất dữ liệu CSV"
        )

@app.post("/import/customers/excel")
async def import_customers_excel(
    file: UploadFile = File(..., description="📁 Excel file với dữ liệu khách hàng"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📥 Import customers from Excel"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File phải có định dạng Excel (.xlsx hoặc .xls)"
            )

        # Read file content
        file_content = await file.read()

        export_service.set_session(db)
        result = export_service.import_customers_from_excel(file_content, current_user.id)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="import",
            resource="customers",
            resource_id=file.filename
        )

        if result["success"]:
            log_business_event(
                event_type="customer_import",
                description=f"Imported {result['success_count']} customers",
                user_id=current_user.id
            )

        return {
            "success": result["success"],
            "message": result.get("message", result.get("error")),
            "data": {
                "success_count": result.get("success_count", 0),
                "error_count": result.get("error_count", 0),
                "errors": result.get("errors", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error importing customers from Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi import dữ liệu khách hàng"
        )

@app.post("/import/products/excel")
async def import_products_excel(
    file: UploadFile = File(..., description="📁 Excel file với dữ liệu sản phẩm"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📥 Import products from Excel"""
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File phải có định dạng Excel (.xlsx hoặc .xls)"
            )

        # Read file content
        file_content = await file.read()

        export_service.set_session(db)
        result = export_service.import_products_from_excel(file_content, current_user.id)

        # Log activity
        log_user_action(
            user_id=str(current_user.id),
            action="import",
            resource="products",
            resource_id=file.filename
        )

        if result["success"]:
            log_business_event(
                event_type="product_import",
                description=f"Imported {result['success_count']} products",
                user_id=current_user.id
            )

        return {
            "success": result["success"],
            "message": result.get("message", result.get("error")),
            "data": {
                "success_count": result.get("success_count", 0),
                "error_count": result.get("error_count", 0),
                "errors": result.get("errors", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ Error importing products from Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi import dữ liệu sản phẩm"
        )

@app.get("/export/stats")
async def get_export_stats(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Get export statistics"""
    try:
        export_service.set_session(db)
        stats = export_service.get_export_stats()

        return {
            "success": True,
            "data": stats,
            "message": "📊 Export statistics retrieved"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting export stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy thống kê export"
        )

# 🔔 WEBSOCKET ENDPOINTS - Real-time notifications!

@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """🔔 WebSocket endpoint for real-time notifications"""
    db = next(get_db())

    try:
        # Verify token and get user
        from auth import verify_websocket_token
        user = await verify_websocket_token(token, db)

        if not user:
            await websocket.close(code=4001, reason="Invalid token")
            return

        # Connect user
        await manager.connect(websocket, user.id, user.vai_tro.value)

        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle ping/pong for connection health
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))

        except WebSocketDisconnect:
            pass

    except Exception as e:
        app_logger.error(f"❌ WebSocket error: {str(e)}")
        await websocket.close(code=4000, reason="Server error")
    finally:
        manager.disconnect(websocket)
        db.close()

@app.get("/notifications/stats")
async def get_notification_stats(
    admin_user: NguoiDung = Depends(get_admin_user)
):
    """📊 Get WebSocket notification statistics (Admin only)"""
    try:
        stats = notification_service.get_stats()

        return {
            "success": True,
            "data": stats,
            "message": "📊 Notification statistics retrieved"
        }

    except Exception as e:
        app_logger.error(f"❌ Error getting notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy thống kê thông báo"
        )

@app.post("/notifications/send")
async def send_custom_notification(
    user_id: int,
    title: str = Query(..., description="📋 Tiêu đề thông báo"),
    message: str = Query(..., description="💬 Nội dung thông báo"),
    admin_user: NguoiDung = Depends(get_admin_user)
):
    """📨 Send custom notification to user (Admin only)"""
    try:
        from websocket_service import send_custom_notification
        await send_custom_notification(user_id, title, message)

        return {
            "success": True,
            "message": f"📨 Đã gửi thông báo đến người dùng {user_id}"
        }

    except Exception as e:
        app_logger.error(f"❌ Error sending notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi gửi thông báo"
        )

@app.post("/notifications/broadcast")
async def broadcast_notification(
    title: str = Query(..., description="📋 Tiêu đề thông báo"),
    message: str = Query(..., description="💬 Nội dung thông báo"),
    priority: str = Query("medium", description="🚨 Mức độ ưu tiên"),
    admin_user: NguoiDung = Depends(get_admin_user)
):
    """📡 Broadcast notification to all users (Admin only)"""
    try:
        from websocket_service import notify_system_alert
        await notify_system_alert("broadcast", message, priority)

        return {
            "success": True,
            "message": "📡 Đã gửi thông báo tới tất cả người dùng"
        }

    except Exception as e:
        app_logger.error(f"❌ Error broadcasting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phát thông báo"
        )

# 📊 ADVANCED ANALYTICS ENDPOINTS - Business Intelligence Platform!

@app.get("/analytics/customer-segmentation")
async def get_customer_segmentation(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🎯 Phân tích phân khúc khách hàng (RFM Analysis)"""
    try:
        analytics = get_analytics_service(db)
        return analytics.customer_segmentation_analysis()
    except Exception as e:
        app_logger.error(f"❌ Error in customer segmentation analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích phân khúc khách hàng"
        )

@app.get("/analytics/sales-performance")
async def get_sales_performance(
    days: int = Query(30, description="📅 Số ngày phân tích", ge=1, le=365),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📈 Phân tích hiệu suất bán hàng theo thời gian"""
    try:
        analytics = get_analytics_service(db)
        return analytics.sales_performance_analysis(days)
    except Exception as e:
        app_logger.error(f"❌ Error in sales performance analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích hiệu suất bán hàng"
        )

@app.get("/analytics/product-intelligence")
async def get_product_intelligence(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🧠 Báo cáo thông minh về sản phẩm"""
    try:
        analytics = get_analytics_service(db)
        return analytics.product_intelligence_report()
    except Exception as e:
        app_logger.error(f"❌ Error in product intelligence analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích thông tin sản phẩm"
        )

@app.get("/analytics/communication-analysis")
async def get_communication_analysis(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📞 Phân tích hiệu quả communication với khách hàng"""
    try:
        analytics = get_analytics_service(db)
        return analytics.customer_communication_analysis()
    except Exception as e:
        app_logger.error(f"❌ Error in communication analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi phân tích communication"
        )

@app.get("/analytics/executive-summary")
async def get_executive_summary(
    manager_user: NguoiDung = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """📋 Báo cáo tổng hợp cho leadership (Manager+ only)"""
    try:
        analytics = get_analytics_service(db)
        return analytics.generate_executive_summary()
    except Exception as e:
        app_logger.error(f"❌ Error in executive summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tạo báo cáo tổng hợp"
        )

# 🤖 AI RECOMMENDATION ENDPOINTS - Artificial Intelligence Platform!

@app.get("/ai/recommend-products/{customer_id}")
async def recommend_products_for_customer(
    customer_id: int,
    limit: int = Query(5, description="🔢 Số sản phẩm gợi ý", ge=1, le=20),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🤖 Gợi ý sản phẩm thông minh cho khách hàng"""
    try:
        ai_engine = get_ai_recommendation_engine(db)
        recommendations = ai_engine.recommend_products_for_customer(customer_id, limit)

        # Log AI recommendation event
        if "recommendations" in recommendations:
            from websocket_service import notify_ai_recommendation
            await notify_ai_recommendation(
                "product_recommendation",
                f"Gợi ý {len(recommendations['recommendations'])} sản phẩm",
                f"Cho khách hàng {recommendations.get('customer_name', 'N/A')}",
                recommendations.get('confidence', 0.5),
                current_user.id
            )

        return recommendations
    except Exception as e:
        app_logger.error(f"❌ Error in AI product recommendation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tạo gợi ý sản phẩm"
        )

@app.get("/ai/recommend-customers/{product_id}")
async def recommend_customers_for_product(
    product_id: int,
    limit: int = Query(10, description="🔢 Số khách hàng gợi ý", ge=1, le=50),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """🎯 Gợi ý khách hàng tiềm năng cho sản phẩm"""
    try:
        ai_engine = get_ai_recommendation_engine(db)
        recommendations = ai_engine.recommend_customers_for_product(product_id, limit)

        return recommendations
    except Exception as e:
        app_logger.error(f"❌ Error in AI customer recommendation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi gợi ý khách hàng tiềm năng"
        )

@app.get("/ai/business-insights")
async def get_ai_business_insights(
    manager_user: NguoiDung = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """💡 AI Business Insights và gợi ý chiến lược (Manager+ only)"""
    try:
        ai_engine = get_ai_recommendation_engine(db)
        insights = ai_engine.generate_business_insights()

        # Notify about new insights
        if insights.get('insights'):
            from websocket_service import notify_ai_recommendation
            await notify_ai_recommendation(
                "business_insights",
                f"Có {len(insights['insights'])} insights mới",
                "AI đã phân tích và tạo gợi ý kinh doanh",
                0.8
            )

        return insights
    except Exception as e:
        app_logger.error(f"❌ Error in AI business insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tạo business insights"
        )

# 📄 ADVANCED EXPORT ENDPOINTS - Professional Reports Generator!

@app.get("/export/customers-excel")
async def export_customers_excel(
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📊 Xuất danh sách khách hàng ra Excel"""
    try:
        export_service = get_advanced_export_service(db)
        result = export_service.export_customers_excel()

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except Exception as e:
        app_logger.error(f"❌ Error exporting customers Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất Excel khách hàng"
        )

@app.get("/export/orders-excel")
async def export_orders_excel(
    date_from: Optional[str] = Query(None, description="📅 Ngày bắt đầu (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="📅 Ngày kết thúc (YYYY-MM-DD)"),
    current_user: NguoiDung = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """📋 Xuất danh sách đơn hàng ra Excel"""
    try:
        export_service = get_advanced_export_service(db)
        result = export_service.export_orders_excel(date_from, date_to)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except Exception as e:
        app_logger.error(f"❌ Error exporting orders Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất Excel đơn hàng"
        )

@app.get("/export/analytics-pdf")
async def export_analytics_pdf(
    report_type: str = Query("monthly", description="📊 Loại báo cáo"),
    manager_user: NguoiDung = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """📄 Tạo báo cáo PDF analytics (Manager+ only)"""
    try:
        export_service = get_advanced_export_service(db)
        result = export_service.generate_analytics_pdf_report(report_type)

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return result
    except Exception as e:
        app_logger.error(f"❌ Error generating PDF report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi tạo báo cáo PDF"
        )

@app.get("/export/business-intelligence")
async def export_business_intelligence(
    manager_user: NguoiDung = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """🧠 Xuất báo cáo Business Intelligence toàn diện (Manager+ only)"""
    try:
        export_service = get_advanced_export_service(db)
        result = export_service.export_business_intelligence_excel()

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        # Notify about BI report generation
        from websocket_service import notify_business_milestone
        await notify_business_milestone(
            "bi_report_generated",
            "Báo cáo Business Intelligence đã được tạo",
            "Excel",
            {"sheets": result.get("sheets_included", []), "user": manager_user.ho_ten}
        )

        return result
    except Exception as e:
        app_logger.error(f"❌ Error exporting BI Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi xuất BI Excel"
        )

# 🔍 PERFORMANCE MONITORING ENDPOINTS - APM Dashboard!

@app.get("/monitor/health")
async def get_system_health(
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """🏥 Báo cáo sức khỏe hệ thống toàn diện (Admin only)"""
    try:
        monitor = get_performance_monitor()
        health_report = monitor.generate_health_report(db)
        return health_report
    except Exception as e:
        app_logger.error(f"❌ Error getting system health: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy thông tin sức khỏe hệ thống"
        )

@app.get("/monitor/metrics")
async def get_system_metrics(
    admin_user: NguoiDung = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """📊 Metrics hệ thống chi tiết (Admin only)"""
    try:
        monitor = get_performance_monitor()
        system_metrics = monitor.collect_system_metrics()
        db_metrics = monitor.get_database_metrics(db)

        return {
            "system": system_metrics,
            "database": db_metrics,
            "collected_at": datetime.now().isoformat()
        }
    except Exception as e:
        app_logger.error(f"❌ Error collecting system metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi thu thập system metrics"
        )

@app.get("/monitor/prometheus", response_class=Response)
async def get_prometheus_metrics(admin_user: NguoiDung = Depends(get_admin_user)):
    """📈 Prometheus metrics endpoint (Admin only)"""
    try:
        from performance_monitor import PROMETHEUS_AVAILABLE
        if not PROMETHEUS_AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Prometheus client không khả dụng"
            )

        monitor = get_performance_monitor()
        metrics_data = monitor.get_prometheus_metrics()

        return Response(
            content=metrics_data,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        app_logger.error(f"❌ Error getting Prometheus metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy Prometheus metrics"
        )

@app.get("/monitor/alerts")
async def get_active_alerts(
    admin_user: NguoiDung = Depends(get_admin_user)
):
    """⚠️ Danh sách cảnh báo đang hoạt động (Admin only)"""
    try:
        monitor = get_performance_monitor()
        current_metrics = monitor.collect_system_metrics()
        alerts = monitor.check_alert_conditions(current_metrics)

        return {
            "active_alerts": alerts,
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a.get('severity') == 'critical']),
            "warning_alerts": len([a for a in alerts if a.get('severity') == 'warning']),
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        app_logger.error(f"❌ Error getting alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lỗi khi lấy danh sách cảnh báo"
        )

# 🚀 API siêu đỉnh đã hoàn thành!
# Giờ có thể quản lý CRM như một ông hoàng! 👑

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FADO CRM API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)