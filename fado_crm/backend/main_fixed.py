# -*- coding: utf-8 -*-
# FADO CRM - FastAPI Backend Sieu Toc! (Fixed Version)

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import os

# Import core modules
from database import get_db, create_tables
from models import KhachHang, SanPham, DonHang, TrangThaiDonHang, LoaiKhachHang

# Simple response models
class MessageResponse(BaseModel):
    message: str
    success: bool

class ThongKeResponse(BaseModel):
    tong_khach_hang: int
    tong_don_hang: int
    doanh_thu_thang: float
    don_cho_xu_ly: int
    khach_moi_thang: int

# Simple logger
class SimpleLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")

app_logger = SimpleLogger()

# Initialize FastAPI app
app = FastAPI(
    title="FADO.VN CRM API",
    description="API CRM cho nganh mua ho - Fixed Version",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
@app.get("/", response_model=MessageResponse)
async def root():
    """Endpoint chao mung - Hello World phien ban sieu xin!"""
    return MessageResponse(
        message="Chao mung den voi FADO.VN CRM API! San sang phuc vu!",
        success=True
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
        "version": "1.0.0"
    }

# Dashboard/Thong ke tong quan
@app.get("/dashboard", response_model=ThongKeResponse)
async def get_dashboard(db: Session = Depends(get_db)):
    """Dashboard sieu cool voi thong ke realtime!"""
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    # Tinh toan cac chi so
    tong_khach_hang = db.query(KhachHang).count()
    tong_don_hang = db.query(DonHang).count()

    # Doanh thu thang nay
    doanh_thu_thang = db.query(func.sum(DonHang.tong_tien)).filter(
        DonHang.ngay_tao >= start_of_month,
        DonHang.trang_thai != TrangThaiDonHang.HUY
    ).scalar() or 0.0

    # Don cho xu ly
    don_cho_xu_ly = db.query(DonHang).filter(
        DonHang.trang_thai.in_([
            TrangThaiDonHang.CHO_XAC_NHAN,
            TrangThaiDonHang.DA_XAC_NHAN,
            TrangThaiDonHang.DANG_MUA
        ])
    ).count()

    # Khach moi thang nay
    khach_moi_thang = db.query(KhachHang).filter(
        KhachHang.ngay_tao >= start_of_month
    ).count()

    return ThongKeResponse(
        tong_khach_hang=tong_khach_hang,
        tong_don_hang=tong_don_hang,
        doanh_thu_thang=doanh_thu_thang,
        don_cho_xu_ly=don_cho_xu_ly,
        khach_moi_thang=khach_moi_thang
    )

# KHACH HANG ENDPOINTS
@app.get("/khach-hang/")
async def get_khach_hang_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lay danh sach khach hang"""
    query = db.query(KhachHang)

    if search:
        query = query.filter(
            (KhachHang.ho_ten.contains(search)) |
            (KhachHang.email.contains(search)) |
            (KhachHang.so_dien_thoai.contains(search))
        )

    khach_hang_list = query.offset(skip).limit(limit).all()

    # Convert to dict for JSON response
    result = []
    for kh in khach_hang_list:
        result.append({
            "id": kh.id,
            "ho_ten": kh.ho_ten,
            "email": kh.email,
            "so_dien_thoai": kh.so_dien_thoai,
            "dia_chi": kh.dia_chi,
            "loai": kh.loai.value if kh.loai else None,
            "ngay_tao": kh.ngay_tao.isoformat() if kh.ngay_tao else None
        })

    return {"data": result, "total": len(result)}

@app.get("/khach-hang/{khach_hang_id}")
async def get_khach_hang(khach_hang_id: int, db: Session = Depends(get_db)):
    """Lay thong tin khach hang theo ID"""
    khach_hang = db.query(KhachHang).filter(KhachHang.id == khach_hang_id).first()
    if not khach_hang:
        raise HTTPException(status_code=404, detail="Khong tim thay khach hang")

    return {
        "id": khach_hang.id,
        "ho_ten": khach_hang.ho_ten,
        "email": khach_hang.email,
        "so_dien_thoai": khach_hang.so_dien_thoai,
        "dia_chi": khach_hang.dia_chi,
        "loai": khach_hang.loai.value if khach_hang.loai else None,
        "ngay_tao": khach_hang.ngay_tao.isoformat() if khach_hang.ngay_tao else None
    }

# SAN PHAM ENDPOINTS
@app.get("/san-pham/")
async def get_san_pham_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lay danh sach san pham"""
    query = db.query(SanPham)

    if search:
        query = query.filter(SanPham.ten.contains(search))

    san_pham_list = query.offset(skip).limit(limit).all()

    result = []
    for sp in san_pham_list:
        result.append({
            "id": sp.id,
            "ten": sp.ten,
            "mo_ta": sp.mo_ta,
            "gia_goc": float(sp.gia_goc) if sp.gia_goc else None,
            "gia_ban": float(sp.gia_ban) if sp.gia_ban else None,
            "danh_muc": sp.danh_muc,
            "ngay_tao": sp.ngay_tao.isoformat() if sp.ngay_tao else None
        })

    return {"data": result, "total": len(result)}

# DON HANG ENDPOINTS
@app.get("/don-hang/")
async def get_don_hang_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    trang_thai: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Lay danh sach don hang"""
    query = db.query(DonHang)

    if trang_thai:
        try:
            trang_thai_enum = TrangThaiDonHang(trang_thai)
            query = query.filter(DonHang.trang_thai == trang_thai_enum)
        except ValueError:
            pass  # Invalid status, ignore filter

    don_hang_list = query.order_by(DonHang.ngay_tao.desc()).offset(skip).limit(limit).all()

    result = []
    for dh in don_hang_list:
        result.append({
            "id": dh.id,
            "ma_don_hang": dh.ma_don_hang,
            "khach_hang_id": dh.khach_hang_id,
            "tong_tien": float(dh.tong_tien) if dh.tong_tien else None,
            "trang_thai": dh.trang_thai.value if dh.trang_thai else None,
            "ghi_chu": dh.ghi_chu,
            "ngay_tao": dh.ngay_tao.isoformat() if dh.ngay_tao else None
        })

    return {"data": result, "total": len(result)}

@app.get("/don-hang/{don_hang_id}")
async def get_don_hang(don_hang_id: int, db: Session = Depends(get_db)):
    """Lay thong tin don hang theo ID"""
    don_hang = db.query(DonHang).filter(DonHang.id == don_hang_id).first()
    if not don_hang:
        raise HTTPException(status_code=404, detail="Khong tim thay don hang")

    return {
        "id": don_hang.id,
        "ma_don_hang": don_hang.ma_don_hang,
        "khach_hang_id": don_hang.khach_hang_id,
        "tong_tien": float(don_hang.tong_tien) if don_hang.tong_tien else None,
        "trang_thai": don_hang.trang_thai.value if don_hang.trang_thai else None,
        "ghi_chu": don_hang.ghi_chu,
        "ngay_tao": don_hang.ngay_tao.isoformat() if don_hang.ngay_tao else None
    }

# AUTH ENDPOINTS - Simple authentication
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str = None
    user: dict = None

@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Simple login endpoint for testing"""
    # Demo credentials
    if login_data.email == "admin@fado.vn" and login_data.password == "admin123":
        return LoginResponse(
            success=True,
            message="Đăng nhập thành công!",
            token="demo-jwt-token-123",
            user={
                "id": 1,
                "email": "admin@fado.vn",
                "ho_ten": "Admin FADO",
                "vai_tro": "admin"
            }
        )
    else:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")

@app.get("/auth/me")
async def get_current_user():
    """Get current user info"""
    return {
        "id": 1,
        "email": "admin@fado.vn",
        "ho_ten": "Admin FADO",
        "vai_tro": "admin"
    }

@app.post("/auth/logout")
async def logout():
    """Logout endpoint"""
    return {"success": True, "message": "Đăng xuất thành công"}

# Test endpoints for basic functionality
@app.get("/test/status")
async def test_status():
    """Test endpoint to verify API is working"""
    return {
        "status": "FADO CRM API is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0-fixed"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
