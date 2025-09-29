# FADO.VN CRM - Database Models
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Enum
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# Enum for order status
class TrangThaiDonHang(enum.Enum):
    CHO_XAC_NHAN = "cho_xac_nhan"
    DA_XAC_NHAN = "da_xac_nhan"
    DANG_MUA = "dang_mua"
    DA_MUA = "da_mua"
    DANG_SHIP = "dang_ship"
    DA_NHAN = "da_nhan"
    HUY = "huy"

class LoaiKhachHang(enum.Enum):
    MOI = "moi"
    THAN_THIET = "than_thiet"
    VIP = "vip"
    BLACKLIST = "blacklist"

# Enum for user roles
class VaiTro(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

# Customer Model
class KhachHang(Base):
    __tablename__ = "khach_hang"

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    so_dien_thoai = Column(String(20))
    dia_chi = Column(Text)
    ngay_tao = Column(DateTime, default=datetime.utcnow)
    loai_khach = Column(Enum(LoaiKhachHang), default=LoaiKhachHang.MOI)
    tong_tien_da_mua = Column(Float, default=0.0)
    so_don_thanh_cong = Column(Integer, default=0)
    ghi_chu = Column(Text)

    # Relationships
    don_hang_list = relationship("DonHang", back_populates="khach_hang")

# Product Model
class SanPham(Base):
    __tablename__ = "san_pham"

    id = Column(Integer, primary_key=True, index=True)
    ten_san_pham = Column(String(200), nullable=False)
    link_goc = Column(String(500))
    gia_goc = Column(Float)
    gia_ban = Column(Float)
    mo_ta = Column(Text)
    hinh_anh_url = Column(String(500))
    trong_luong = Column(Float)
    kich_thuoc = Column(String(100))
    danh_muc = Column(String(100))
    quoc_gia_nguon = Column(String(50))
    ngay_tao = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    chi_tiet_don_hang = relationship("ChiTietDonHang", back_populates="san_pham")

# Order Model
class DonHang(Base):
    __tablename__ = "don_hang"

    id = Column(Integer, primary_key=True, index=True)
    ma_don_hang = Column(String(20), unique=True, index=True)
    khach_hang_id = Column(Integer, ForeignKey("khach_hang.id"))

    # Financial information
    tong_gia_san_pham = Column(Float, default=0.0)
    phi_mua_ho = Column(Float, default=0.0)
    phi_van_chuyen = Column(Float, default=0.0)
    phi_khac = Column(Float, default=0.0)
    tong_tien = Column(Float, default=0.0)

    # Status and timing
    trang_thai = Column(Enum(TrangThaiDonHang), default=TrangThaiDonHang.CHO_XAC_NHAN)
    ngay_tao = Column(DateTime, default=datetime.utcnow)
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow)
    ngay_giao_hang = Column(DateTime)

    # Additional info
    ghi_chu_khach = Column(Text)
    ghi_chu_noi_bo = Column(Text)
    ma_van_don = Column(String(50))

    # Relationships
    khach_hang = relationship("KhachHang", back_populates="don_hang_list")
    chi_tiet_list = relationship("ChiTietDonHang", back_populates="don_hang")

# Order Detail Model
class ChiTietDonHang(Base):
    __tablename__ = "chi_tiet_don_hang"

    id = Column(Integer, primary_key=True, index=True)
    don_hang_id = Column(Integer, ForeignKey("don_hang.id"))
    san_pham_id = Column(Integer, ForeignKey("san_pham.id"))
    so_luong = Column(Integer, default=1)
    gia_mua = Column(Float)
    ghi_chu = Column(Text)

    # Relationships
    don_hang = relationship("DonHang", back_populates="chi_tiet_list")
    san_pham = relationship("SanPham", back_populates="chi_tiet_don_hang")

# Contact History Model
class LichSuLienHe(Base):
    __tablename__ = "lich_su_lien_he"

    id = Column(Integer, primary_key=True, index=True)
    khach_hang_id = Column(Integer, ForeignKey("khach_hang.id"))
    loai_lien_he = Column(String(50))
    noi_dung = Column(Text)
    ngay_lien_he = Column(DateTime, default=datetime.utcnow)
    nhan_vien_xu_ly = Column(String(100))
    ket_qua = Column(String(200))

    # Relationships
    khach_hang = relationship("KhachHang")

# User Model
class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    ho_ten = Column(String(100), nullable=False)
    mat_khau_hash = Column(String(255), nullable=False)
    vai_tro = Column(Enum(VaiTro), default=VaiTro.STAFF)
    is_active = Column(Boolean, default=True)
    ngay_tao = Column(DateTime, default=datetime.utcnow)
    lan_dang_nhap_cuoi = Column(DateTime)
    so_dien_thoai = Column(String(20))
    ghi_chu = Column(Text)

# Audit Log
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False)
    resource = Column(String(50), nullable=False)
    resource_id = Column(String(100))
    user_id = Column(Integer, nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# System Settings
class SystemSetting(Base):
    __tablename__ = "system_setting"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow)

# Payment Status
class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

# Payment Transactions
class PaymentTransaction(Base):
    __tablename__ = "payment_transaction"

    transaction_id = Column(String(64), primary_key=True)
    don_hang_id = Column(Integer, ForeignKey("don_hang.id"), nullable=False)
    payment_method = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="VND")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    gateway_reference = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)