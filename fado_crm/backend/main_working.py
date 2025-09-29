# -*- coding: utf-8 -*-
# FADO CRM - FastAPI Backend Sieu Toc!
# API nay nhanh nhu tia chop va manh nhu Thor!

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import schemas

# Import core modules
from database import create_tables, get_db
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import DonHang, KhachHang, LoaiKhachHang, SanPham, TrangThaiDonHang
from sqlalchemy import func, text
from sqlalchemy.orm import Session

# Import error handling & logging
try:
    from exceptions import format_success_response
    from logging_config import app_logger
    from middleware import (
        ErrorHandlerMiddleware,
        RequestLoggingMiddleware,
        SecurityHeadersMiddleware,
    )

    MIDDLEWARE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MIDDLEWARE_AVAILABLE = False

    # Create dummy logger
    class DummyLogger:
        def info(self, msg):
            print(f"INFO: {msg}")

        def error(self, msg):
            print(f"ERROR: {msg}")

    app_logger = DummyLogger()

# Optional imports with error handling
try:
    from auth import get_admin_user, get_current_active_user, login_user, refresh_access_token

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False
    print("Warning: Auth module not available")

try:
    from analytics_service import get_analytics_data

    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    print("Warning: Analytics service not available")

# Initialize FastAPI app
app = FastAPI(
    title="FADO.VN CRM API",
    description="API CRM cho nganh mua ho - Code boi AI voi tinh yeu!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware (if available)
if MIDDLEWARE_AVAILABLE:
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Startup event
@app.on_event("startup")
async def startup_event():
    app_logger.info("Starting FADO CRM API...")
    try:
        create_tables()
        app_logger.info("Database tables created successfully")
        app_logger.info("FADO CRM API is ready to serve!")
    except Exception as e:
        app_logger.error(f"Failed to start API: {str(e)}")
        raise


# Root endpoint
@app.get("/", response_model=schemas.MessageResponse)
async def root():
    """Endpoint chao mung - Hello World phien ban sieu xin!"""
    return schemas.MessageResponse(
        message="Chao mung den voi FADO.VN CRM API! San sang phuc vu!", success=True
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    db_ok = False
    db_error = None
    try:
        from database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_error = str(e)

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else {"status": "error", "error": db_error},
        "auth_available": AUTH_AVAILABLE,
        "analytics_available": ANALYTICS_AVAILABLE,
        "version": "1.0.0",
    }


# AUTHENTICATION ENDPOINTS
@app.post("/auth/login", response_model=schemas.LoginResponse)
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Dang nhap va lay JWT token (su dung auth.login_user)"""
    try:
        result = login_user(db, login_data.email, login_data.password)
        return schemas.LoginResponse(**result)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email hoac mat khau khong chinh xac"
        )


@app.post("/auth/refresh", response_model=schemas.TokenResponse)
async def refresh_token(refresh_data: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        result = refresh_access_token(refresh_data.refresh_token, db)
        return schemas.TokenResponse(**result)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token khong hop le"
        )


@app.get("/auth/me", response_model=schemas.NguoiDung)
async def get_current_user_info(current_user=Depends(get_current_active_user)):
    return current_user


# Dashboard/Thong ke tong quan
@app.get("/dashboard", response_model=schemas.ThongKeResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """Dashboard sieu cool voi thong ke realtime!"""
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    # Tinh toan cac chi so
    tong_khach_hang = db.query(KhachHang).count()
    tong_don_hang = db.query(DonHang).count()

    # Doanh thu thang nay
    doanh_thu_thang = (
        db.query(func.sum(DonHang.tong_tien))
        .filter(DonHang.ngay_tao >= start_of_month, DonHang.trang_thai != TrangThaiDonHang.HUY)
        .scalar()
        or 0.0
    )

    # Don cho xu ly
    don_cho_xu_ly = (
        db.query(DonHang)
        .filter(
            DonHang.trang_thai.in_(
                [
                    TrangThaiDonHang.CHO_XAC_NHAN,
                    TrangThaiDonHang.DA_XAC_NHAN,
                    TrangThaiDonHang.DANG_MUA,
                ]
            )
        )
        .count()
    )

    # Khach moi thang nay
    khach_moi_thang = db.query(KhachHang).filter(KhachHang.ngay_tao >= start_of_month).count()

    return schemas.ThongKeResponse(
        tong_khach_hang=tong_khach_hang,
        tong_don_hang=tong_don_hang,
        doanh_thu_thang=doanh_thu_thang,
        don_cho_xu_ly=don_cho_xu_ly,
        khach_moi_thang=khach_moi_thang,
    )


# KHACH HANG ENDPOINTS
@app.get("/khach-hang/", response_model=List[schemas.KhachHang])
async def get_khach_hang_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lay danh sach khach hang"""
    query = db.query(KhachHang)

    if search:
        query = query.filter(
            (KhachHang.ho_ten.contains(search))
            | (KhachHang.email.contains(search))
            | (KhachHang.so_dien_thoai.contains(search))
        )

    khach_hang_list = query.offset(skip).limit(limit).all()
    return khach_hang_list


@app.post("/khach-hang/", response_model=schemas.KhachHang)
async def create_khach_hang(khach_hang: schemas.KhachHangCreate, db: Session = Depends(get_db)):
    """Tao khach hang moi"""
    # Check if email already exists
    existing = db.query(KhachHang).filter(KhachHang.email == khach_hang.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email da ton tai")

    db_khach_hang = KhachHang(**khach_hang.dict())
    db.add(db_khach_hang)
    db.commit()
    db.refresh(db_khach_hang)
    return db_khach_hang


@app.get("/khach-hang/{khach_hang_id}", response_model=schemas.KhachHang)
async def get_khach_hang(khach_hang_id: int, db: Session = Depends(get_db)):
    """Lay thong tin khach hang theo ID"""
    khach_hang = db.query(KhachHang).filter(KhachHang.id == khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khach hang"
        )
    return khach_hang


@app.put("/khach-hang/{khach_hang_id}", response_model=schemas.KhachHang)
async def update_khach_hang(
    khach_hang_id: int, khach_hang_update: schemas.KhachHangUpdate, db: Session = Depends(get_db)
):
    """Cap nhat thong tin khach hang"""
    khach_hang = db.query(KhachHang).filter(KhachHang.id == khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay khach hang"
        )

    update_data = khach_hang_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(khach_hang, field, value)

    db.commit()
    db.refresh(khach_hang)
    return khach_hang


# SAN PHAM ENDPOINTS
@app.get("/san-pham/", response_model=List[schemas.SanPham])
async def get_san_pham_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lay danh sach san pham"""
    query = db.query(SanPham)

    if search:
        query = query.filter(SanPham.ten.contains(search))

    san_pham_list = query.offset(skip).limit(limit).all()
    return san_pham_list


@app.post("/san-pham/", response_model=schemas.SanPham)
async def create_san_pham(san_pham: schemas.SanPhamCreate, db: Session = Depends(get_db)):
    """Tao san pham moi"""
    db_san_pham = SanPham(**san_pham.dict())
    db.add(db_san_pham)
    db.commit()
    db.refresh(db_san_pham)
    return db_san_pham


# DON HANG ENDPOINTS
@app.get("/don-hang/", response_model=List[schemas.DonHang])
async def get_don_hang_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    trang_thai: Optional[TrangThaiDonHang] = Query(None),
    db: Session = Depends(get_db),
):
    """Lay danh sach don hang"""
    query = db.query(DonHang)

    if trang_thai:
        query = query.filter(DonHang.trang_thai == trang_thai)

    don_hang_list = query.order_by(DonHang.ngay_tao.desc()).offset(skip).limit(limit).all()
    return don_hang_list


@app.post("/don-hang/", response_model=schemas.DonHang)
async def create_don_hang(don_hang: schemas.DonHangCreate, db: Session = Depends(get_db)):
    """Tao don hang moi"""
    # Generate unique order code
    import uuid

    ma_don_hang = f"FADO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

    db_don_hang = DonHang(
        **don_hang.dict(), ma_don_hang=ma_don_hang, trang_thai=TrangThaiDonHang.CHO_XAC_NHAN
    )
    db.add(db_don_hang)
    db.commit()
    db.refresh(db_don_hang)
    return db_don_hang


@app.get("/don-hang/{don_hang_id}", response_model=schemas.DonHang)
async def get_don_hang(don_hang_id: int, db: Session = Depends(get_db)):
    """Lay thong tin don hang theo ID"""
    don_hang = db.query(DonHang).filter(DonHang.id == don_hang_id).first()
    if not don_hang:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay don hang")
    return don_hang


@app.put("/don-hang/{don_hang_id}/trang-thai", response_model=schemas.DonHang)
async def update_don_hang_status(
    don_hang_id: int, trang_thai_update: schemas.TrangThaiUpdate, db: Session = Depends(get_db)
):
    """Cap nhat trang thai don hang"""
    don_hang = db.query(DonHang).filter(DonHang.id == don_hang_id).first()
    if not don_hang:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Khong tim thay don hang")

    don_hang.trang_thai = trang_thai_update.trang_thai
    don_hang.ghi_chu = trang_thai_update.ghi_chu
    db.commit()
    db.refresh(don_hang)
    return don_hang


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
