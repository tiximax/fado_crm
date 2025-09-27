# -*- coding: utf-8 -*-
# FADO CRM - Pydantic Schemas (Reconstructed Minimal)
# Mục tiêu: cung cấp các model cần thiết để server hoạt động ổn định.

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import TrangThaiDonHang, LoaiKhachHang, VaiTro

# Generic message
class MessageResponse(BaseModel):
    message: str
    success: bool = True

# Dashboard stats
class ThongKeResponse(BaseModel):
    tong_khach_hang: int
    tong_don_hang: int
    doanh_thu_thang: float
    don_cho_xu_ly: int
    khach_moi_thang: int

# User schemas
class NguoiDung(BaseModel):
    id: int
    email: EmailStr
    ho_ten: str
    vai_tro: VaiTro
    is_active: bool = True
    ngay_tao: datetime
    lan_dang_nhap_cuoi: Optional[datetime] = None
    class Config:
        from_attributes = True

# Customer
class KhachHang(BaseModel):
    id: int
    ho_ten: str
    email: EmailStr
    so_dien_thoai: Optional[str] = None
    loai_khach: LoaiKhachHang = LoaiKhachHang.MOI
    tong_tien_da_mua: float = 0.0
    so_don_thanh_cong: int = 0
    ngay_tao: datetime
    class Config:
        from_attributes = True

# Product
class SanPham(BaseModel):
    id: int
    ten_san_pham: str
    mo_ta: Optional[str] = None
    danh_muc: Optional[str] = None
    quoc_gia_nguon: Optional[str] = None
    gia_ban: Optional[float] = None
    is_active: bool = True
    ngay_tao: datetime
    class Config:
        from_attributes = True

# Order detail
class ChiTietDonHang(BaseModel):
    id: int
    don_hang_id: int
    san_pham: Optional[SanPham] = None
    so_luong: int
    gia_mua: Optional[float] = None
    class Config:
        from_attributes = True

# Order
class DonHang(BaseModel):
    id: int
    ma_don_hang: str
    khach_hang: Optional[KhachHang] = None
    trang_thai: TrangThaiDonHang
    tong_tien: float
    ngay_tao: datetime
    ngay_cap_nhat: Optional[datetime] = None
    ma_van_don: Optional[str] = None
    chi_tiet_list: List[ChiTietDonHang] = []
    class Config:
        from_attributes = True

# Contact history
class LichSuLienHe(BaseModel):
    id: int
    khach_hang_id: int
    loai_lien_he: str
    noi_dung: str
    nhan_vien_xu_ly: str
    ket_qua: Optional[str] = None
    ngay_lien_he: datetime
    class Config:
        from_attributes = True

# Auth schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: NguoiDung

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# System settings
class SystemSetting(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime
    class Config:
        from_attributes = True

# Payments
class PaymentCreateRequest(BaseModel):
    order_id: int

class PaymentCreateResponse(BaseModel):
    transaction_id: str
    txn_ref: str
    redirect_url: str

# Audit log
class AuditLog(BaseModel):
    id: int
    action: str
    resource: str
    resource_id: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

# Order management enhancements
class OrderStatusUpdate(BaseModel):
    trang_thai: TrangThaiDonHang
    ghi_chu: Optional[str] = None

class ChiTietDonHangCreate(BaseModel):
    san_pham_id: int
    so_luong: int
    gia_mua: Optional[float] = None
    ghi_chu: Optional[str] = None

class OrderDetailsUpdate(BaseModel):
    chi_tiet_list: List[ChiTietDonHangCreate]
