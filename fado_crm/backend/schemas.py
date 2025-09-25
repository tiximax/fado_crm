# 📋 FADO CRM - Pydantic Schemas Siêu Chặt Chẽ!
# Validation như một ninja bảo vệ dữ liệu! 🥷

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from models import TrangThaiDonHang, LoaiKhachHang, VaiTro

# 👥 Schemas cho Khách Hàng
class KhachHangBase(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=100, description="📛 Họ tên khách hàng")
    email: EmailStr = Field(..., description="📧 Email hợp lệ")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="📱 Số điện thoại")
    dia_chi: Optional[str] = Field(None, description="🏠 Địa chỉ nhận hàng")
    loai_khach: Optional[LoaiKhachHang] = Field(LoaiKhachHang.MOI, description="🏷️ Loại khách hàng")
    ghi_chu: Optional[str] = Field(None, description="📝 Ghi chú đặc biệt")

class KhachHangCreate(KhachHangBase):
    """🆕 Schema tạo khách hàng mới - Chào mừng tân binh!"""
    pass

class KhachHangUpdate(BaseModel):
    """🔄 Schema cập nhật thông tin khách hàng"""
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    dia_chi: Optional[str] = None
    loai_khach: Optional[LoaiKhachHang] = None
    ghi_chu: Optional[str] = None

class KhachHang(KhachHangBase):
    """📊 Schema trả về thông tin đầy đủ của khách hàng"""
    id: int
    ngay_tao: datetime
    tong_tien_da_mua: float = Field(0.0, description="💰 Tổng tiền đã chi")
    so_don_thanh_cong: int = Field(0, description="📊 Số đơn thành công")

    class Config:
        from_attributes = True  # Cho phép convert từ SQLAlchemy model

# 🛍️ Schemas cho Sản Phẩm
class SanPhamBase(BaseModel):
    ten_san_pham: str = Field(..., min_length=2, max_length=200, description="🏷️ Tên sản phẩm")
    link_goc: Optional[str] = Field(None, max_length=500, description="🔗 Link gốc")
    gia_goc: Optional[float] = Field(None, ge=0, description="💵 Giá gốc (USD)")
    gia_ban: Optional[float] = Field(None, ge=0, description="💰 Giá bán (VND)")
    mo_ta: Optional[str] = Field(None, description="📋 Mô tả sản phẩm")
    hinh_anh_url: Optional[str] = Field(None, max_length=500, description="🖼️ URL hình ảnh")
    trong_luong: Optional[float] = Field(None, ge=0, description="⚖️ Trọng lượng (kg)")
    kich_thuoc: Optional[str] = Field(None, max_length=100, description="📏 Kích thước")
    danh_muc: Optional[str] = Field(None, max_length=100, description="📂 Danh mục")
    quoc_gia_nguon: Optional[str] = Field(None, max_length=50, description="🌍 Nước xuất xứ")

class SanPhamCreate(SanPhamBase):
    """🆕 Schema tạo sản phẩm mới"""
    pass

class SanPhamUpdate(BaseModel):
    """🔄 Schema cập nhật sản phẩm"""
    ten_san_pham: Optional[str] = Field(None, min_length=2, max_length=200)
    link_goc: Optional[str] = Field(None, max_length=500)
    gia_goc: Optional[float] = Field(None, ge=0)
    gia_ban: Optional[float] = Field(None, ge=0)
    mo_ta: Optional[str] = None
    hinh_anh_url: Optional[str] = Field(None, max_length=500)
    trong_luong: Optional[float] = Field(None, ge=0)
    kich_thuoc: Optional[str] = Field(None, max_length=100)
    danh_muc: Optional[str] = Field(None, max_length=100)
    quoc_gia_nguon: Optional[str] = Field(None, max_length=50)

class SanPham(SanPhamBase):
    """📦 Schema trả về thông tin đầy đủ sản phẩm"""
    id: int
    ngay_tao: datetime

    class Config:
        from_attributes = True

# 📋 Schemas cho Chi Tiết Đơn Hàng
class ChiTietDonHangBase(BaseModel):
    san_pham_id: int = Field(..., gt=0, description="🆔 ID sản phẩm")
    so_luong: int = Field(1, gt=0, description="🔢 Số lượng")
    gia_mua: Optional[float] = Field(None, ge=0, description="💰 Giá mua thực tế")
    ghi_chu: Optional[str] = Field(None, description="📝 Ghi chú")

class ChiTietDonHangCreate(ChiTietDonHangBase):
    """🆕 Schema tạo chi tiết đơn hàng"""
    pass

class ChiTietDonHang(ChiTietDonHangBase):
    """📋 Schema chi tiết đơn hàng với thông tin sản phẩm"""
    id: int
    don_hang_id: int
    san_pham: Optional[SanPham] = None  # 🔗 Thông tin sản phẩm liên kết

    class Config:
        from_attributes = True

# 📋 Schemas cho Đơn Hàng
class DonHangBase(BaseModel):
    khach_hang_id: int = Field(..., gt=0, description="🆔 ID khách hàng")
    tong_gia_san_pham: float = Field(0.0, ge=0, description="💵 Tổng giá sản phẩm")
    phi_mua_ho: float = Field(0.0, ge=0, description="💼 Phí mua hộ")
    phi_van_chuyen: float = Field(0.0, ge=0, description="🚚 Phí vận chuyển")
    phi_khac: float = Field(0.0, ge=0, description="💸 Phí khác")
    ngay_giao_hang: Optional[datetime] = Field(None, description="📦 Ngày giao hàng dự kiến")
    ghi_chu_khach: Optional[str] = Field(None, description="💬 Ghi chú từ khách")
    ghi_chu_noi_bo: Optional[str] = Field(None, description="🔒 Ghi chú nội bộ")

class DonHangCreate(DonHangBase):
    """🆕 Schema tạo đơn hàng mới với danh sách sản phẩm"""
    chi_tiet_list: List[ChiTietDonHangCreate] = Field(..., min_items=1, description="📋 Danh sách sản phẩm")

class DonHangUpdate(BaseModel):
    """🔄 Schema cập nhật đơn hàng"""
    trang_thai: Optional[TrangThaiDonHang] = None
    phi_mua_ho: Optional[float] = Field(None, ge=0)
    phi_van_chuyen: Optional[float] = Field(None, ge=0)
    phi_khac: Optional[float] = Field(None, ge=0)
    ngay_giao_hang: Optional[datetime] = None
    ghi_chu_khach: Optional[str] = None
    ghi_chu_noi_bo: Optional[str] = None
    ma_van_don: Optional[str] = Field(None, max_length=50, description="🚛 Mã vận đơn")

class DonHang(DonHangBase):
    """📊 Schema đơn hàng đầy đủ với tất cả thông tin"""
    id: int
    ma_don_hang: str
    trang_thai: TrangThaiDonHang
    tong_tien: float = Field(description="💰 Tổng tiền cuối cùng")
    ngay_tao: datetime
    ngay_cap_nhat: datetime
    ma_van_don: Optional[str] = None
    khach_hang: Optional[KhachHang] = None  # 🔗 Thông tin khách hàng
    chi_tiet_list: List[ChiTietDonHang] = []  # 📋 Danh sách chi tiết

    class Config:
        from_attributes = True

# 📞 Schemas cho Lịch Sử Liên Hệ
class LichSuLienHeBase(BaseModel):
    khach_hang_id: int = Field(..., gt=0, description="🆔 ID khách hàng")
    loai_lien_he: str = Field(..., description="📞 Loại liên hệ: call/sms/email")
    noi_dung: str = Field(..., min_length=1, description="💬 Nội dung cuộc liên hệ")
    nhan_vien_xu_ly: str = Field(..., max_length=100, description="👨‍💼 Nhân viên xử lý")
    ket_qua: Optional[str] = Field(None, max_length=200, description="✅ Kết quả")

class LichSuLienHeCreate(LichSuLienHeBase):
    """🆕 Schema tạo lịch sử liên hệ mới"""
    pass

class LichSuLienHe(LichSuLienHeBase):
    """📞 Schema lịch sử liên hệ đầy đủ"""
    id: int
    ngay_lien_he: datetime

    class Config:
        from_attributes = True

# 📊 Schema cho Dashboard/Thống kê
class ThongKeResponse(BaseModel):
    """📊 Schema cho dashboard thống kê siêu cool!"""
    tong_khach_hang: int = Field(description="👥 Tổng số khách hàng")
    tong_don_hang: int = Field(description="📋 Tổng số đơn hàng")
    doanh_thu_thang: float = Field(description="💰 Doanh thu tháng này")
    don_cho_xu_ly: int = Field(description="⏳ Đơn chờ xử lý")
    khach_moi_thang: int = Field(description="🆕 Khách mới tháng này")

# 🎯 Response cho API calls
class MessageResponse(BaseModel):
    """💬 Schema cho message response chung"""
    message: str = Field(description="📢 Thông báo")
    success: bool = Field(True, description="✅ Trạng thái thành công")

# 🔐 Authentication Schemas - Bảo mật cấp độ NASA!
class LoginRequest(BaseModel):
    """🎪 Schema cho đăng nhập"""
    email: EmailStr = Field(..., description="📧 Email đăng nhập")
    password: str = Field(..., min_length=6, description="🔒 Mật khẩu")

class LoginResponse(BaseModel):
    """🎫 Schema cho phản hồi đăng nhập"""
    access_token: str = Field(..., description="🎫 JWT Access Token")
    refresh_token: str = Field(..., description="🔄 JWT Refresh Token")
    token_type: str = Field("bearer", description="🏷️ Loại token")
    expires_in: int = Field(..., description="⏰ Thời gian hết hạn (giây)")
    user: 'NguoiDung' = Field(..., description="👤 Thông tin người dùng")

class RefreshTokenRequest(BaseModel):
    """🔄 Schema cho refresh token"""
    refresh_token: str = Field(..., description="🔄 Refresh token")

class TokenResponse(BaseModel):
    """🎫 Schema cho phản hồi token mới"""
    access_token: str = Field(..., description="🎫 JWT Access Token mới")
    token_type: str = Field("bearer", description="🏷️ Loại token")
    expires_in: int = Field(..., description="⏰ Thời gian hết hạn (giây)")

class ChangePasswordRequest(BaseModel):
    """🔐 Schema đổi mật khẩu"""
    old_password: str = Field(..., min_length=6, description="🔒 Mật khẩu cũ")
    new_password: str = Field(..., min_length=6, description="🆕 Mật khẩu mới")

# 👤 Schemas cho Người Dùng
class NguoiDungBase(BaseModel):
    """👤 Schema cơ bản cho người dùng"""
    email: EmailStr = Field(..., description="📧 Email đăng nhập")
    ho_ten: str = Field(..., min_length=2, max_length=100, description="📛 Họ tên")
    so_dien_thoai: Optional[str] = Field(None, max_length=20, description="📱 Số điện thoại")
    vai_tro: Optional[VaiTro] = Field(VaiTro.STAFF, description="🎭 Vai trò")
    ghi_chu: Optional[str] = Field(None, description="📝 Ghi chú")

class NguoiDungCreate(NguoiDungBase):
    """🆕 Schema tạo người dùng mới"""
    password: str = Field(..., min_length=6, description="🔒 Mật khẩu")

class NguoiDungUpdate(BaseModel):
    """🔄 Schema cập nhật người dùng"""
    ho_ten: Optional[str] = Field(None, min_length=2, max_length=100)
    so_dien_thoai: Optional[str] = Field(None, max_length=20)
    vai_tro: Optional[VaiTro] = None
    is_active: Optional[bool] = None
    ghi_chu: Optional[str] = None

class NguoiDung(NguoiDungBase):
    """👤 Schema người dùng đầy đủ"""
    id: int
    is_active: bool = True
    ngay_tao: datetime
    lan_dang_nhap_cuoi: Optional[datetime] = None

    class Config:
        from_attributes = True

# ⚙️ System Settings Schemas
class SystemSettingBase(BaseModel):
    description: Optional[str] = Field(None, max_length=255)

class SystemSettingUpdate(SystemSettingBase):
    value: str = Field(..., description="Giá trị cấu hình")

class SystemSetting(SystemSettingBase):
    key: str
    value: str
    updated_at: datetime

    class Config:
        from_attributes = True

# 💳 Payments Schemas
class PaymentCreateRequest(BaseModel):
    order_id: int = Field(..., gt=0)

class PaymentCreateResponse(BaseModel):
    transaction_id: str
    txn_ref: str
    redirect_url: str

# 📝 Audit Log Schemas
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

# 🚀 Xong rồi! Schemas chặt chẽ như Fort Knox!
# Giờ có thể validate dữ liệu như một pro security! 🛡️
