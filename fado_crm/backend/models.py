# 🚀 FADO.VN CRM - Models Database Siêu Xịn!
# Được code bởi AI rocker với đầy tình yêu và cafein ☕

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# 🎯 Enum cho trạng thái đơn hàng - Này là siêu quan trọng đấy!
class TrangThaiDonHang(enum.Enum):
    CHO_XAC_NHAN = "cho_xac_nhan"      # 📋 Chờ xác nhận
    DA_XAC_NHAN = "da_xac_nhan"        # ✅ Đã xác nhận
    DANG_MUA = "dang_mua"              # 🛒 Đang mua hàng
    DA_MUA = "da_mua"                  # 💰 Đã mua xong
    DANG_SHIP = "dang_ship"            # 🚚 Đang vận chuyển
    DA_NHAN = "da_nhan"                # 📦 Đã nhận hàng
    HUY = "huy"                        # ❌ Huỷ đơn

class LoaiKhachHang(enum.Enum):
    MOI = "moi"                        # 🆕 Khách mới toanh
    THAN_THIET = "than_thiet"          # 💎 Khách thân thiết
    VIP = "vip"                        # 👑 Khách VIP
    BLACKLIST = "blacklist"            # 🚫 Khách đen

# 🎭 Enum cho vai trò người dùng - Phân quyền siêu chặt!
class VaiTro(enum.Enum):
    ADMIN = "admin"                    # 👑 Quản trị viên tối cao
    MANAGER = "manager"                # 👨‍💼 Quản lý
    STAFF = "staff"                    # 👨‍💻 Nhân viên
    VIEWER = "viewer"                  # 👁️ Chỉ xem

# 👥 Model Khách Hàng - Đây là trái tim của CRM!
class KhachHang(Base):
    __tablename__ = "khach_hang"

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String(100), nullable=False)           # 📛 Họ tên khách
    email = Column(String(100), unique=True, index=True)   # 📧 Email liên hệ
    so_dien_thoai = Column(String(20))                     # 📱 Số điện thoại
    dia_chi = Column(Text)                                 # 🏠 Địa chỉ nhận hàng
    ngay_tao = Column(DateTime, default=datetime.utcnow)   # 📅 Ngày tạo tài khoản
    loai_khach = Column(Enum(LoaiKhachHang), default=LoaiKhachHang.MOI)  # 🏷️ Phân loại khách
    tong_tien_da_mua = Column(Float, default=0.0)         # 💰 Tổng tiền đã chi
    so_don_thanh_cong = Column(Integer, default=0)        # 📊 Số đơn thành công
    ghi_chu = Column(Text)                                 # 📝 Ghi chú đặc biệt

    # 🔗 Liên kết với các đơn hàng
    don_hang_list = relationship("DonHang", back_populates="khach_hang")

# 🛍️ Model Sản Phẩm - Những món hàng xịn sò từ nước ngoài!
class SanPham(Base):
    __tablename__ = "san_pham"

    id = Column(Integer, primary_key=True, index=True)
    ten_san_pham = Column(String(200), nullable=False)     # 🏷️ Tên sản phẩm
    link_goc = Column(String(500))                         # 🔗 Link gốc từ shop nước ngoài
    gia_goc = Column(Float)                                # 💵 Giá gốc (USD)
    gia_ban = Column(Float)                                # 💰 Giá bán (VND)
    mo_ta = Column(Text)                                   # 📋 Mô tả sản phẩm
    hinh_anh_url = Column(String(500))                     # 🖼️ Link hình ảnh
    trong_luong = Column(Float)                            # ⚖️ Trọng lượng (kg)
    kich_thuoc = Column(String(100))                       # 📏 Kích thước
    danh_muc = Column(String(100))                         # 📂 Danh mục
    quoc_gia_nguon = Column(String(50))                    # 🌍 Nước xuất xứ
    ngay_tao = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)              # 🔄 Trạng thái hoạt động (soft delete)

    # 🔗 Liên kết với chi tiết đơn hàng
    chi_tiet_don_hang = relationship("ChiTietDonHang", back_populates="san_pham")

# 📋 Model Đơn Hàng - Trái tim của việc mua hộ!
class DonHang(Base):
    __tablename__ = "don_hang"

    id = Column(Integer, primary_key=True, index=True)
    ma_don_hang = Column(String(20), unique=True, index=True)  # 🔢 Mã đơn duy nhất
    khach_hang_id = Column(Integer, ForeignKey("khach_hang.id"))

    # 💰 Thông tin tài chính siêu quan trọng
    tong_gia_san_pham = Column(Float, default=0.0)        # 💵 Tổng giá sản phẩm
    phi_mua_ho = Column(Float, default=0.0)               # 💼 Phí mua hộ
    phi_van_chuyen = Column(Float, default=0.0)           # 🚚 Phí vận chuyển
    phi_khac = Column(Float, default=0.0)                 # 💸 Phí khác
    tong_tien = Column(Float, default=0.0)                # 💰 Tổng tiền cuối cùng

    # 📊 Trạng thái và thời gian
    trang_thai = Column(Enum(TrangThaiDonHang), default=TrangThaiDonHang.CHO_XAC_NHAN)
    ngay_tao = Column(DateTime, default=datetime.utcnow)   # 📅 Ngày tạo đơn
    ngay_cap_nhat = Column(DateTime, default=datetime.utcnow)  # 🔄 Lần cập nhật cuối
    ngay_giao_hang = Column(DateTime)                      # 📦 Ngày giao hàng dự kiến

    # 📝 Thông tin bổ sung
    ghi_chu_khach = Column(Text)                          # 💬 Ghi chú từ khách hàng
    ghi_chu_noi_bo = Column(Text)                         # 🔒 Ghi chú nội bộ
    ma_van_don = Column(String(50))                       # 🚛 Mã vận đơn

    # 🔗 Liên kết
    khach_hang = relationship("KhachHang", back_populates="don_hang_list")
    chi_tiet_list = relationship("ChiTietDonHang", back_populates="don_hang")

# 📋 Model Chi Tiết Đơn Hàng - Từng sản phẩm trong đơn
class ChiTietDonHang(Base):
    __tablename__ = "chi_tiet_don_hang"

    id = Column(Integer, primary_key=True, index=True)
    don_hang_id = Column(Integer, ForeignKey("don_hang.id"))
    san_pham_id = Column(Integer, ForeignKey("san_pham.id"))

    so_luong = Column(Integer, default=1)                 # 🔢 Số lượng
    gia_mua = Column(Float)                               # 💰 Giá mua thực tế
    ghi_chu = Column(Text)                                # 📝 Ghi chú riêng

    # 🔗 Liên kết
    don_hang = relationship("DonHang", back_populates="chi_tiet_list")
    san_pham = relationship("SanPham", back_populates="chi_tiet_don_hang")

# 📞 Model Lịch Sử Liên Hệ - Tracking mọi cuộc gọi và tin nhắn
class LichSuLienHe(Base):
    __tablename__ = "lich_su_lien_he"

    id = Column(Integer, primary_key=True, index=True)
    khach_hang_id = Column(Integer, ForeignKey("khach_hang.id"))
    loai_lien_he = Column(String(50))                     # 📞 call, 💬 sms, 📧 email
    noi_dung = Column(Text)                               # 💬 Nội dung cuộc liên hệ
    ngay_lien_he = Column(DateTime, default=datetime.utcnow)
    nhan_vien_xu_ly = Column(String(100))                 # 👨‍💼 Nhân viên xử lý
    ket_qua = Column(String(200))                         # ✅ Kết quả liên hệ

    # 🔗 Liên kết ngược về khách hàng
    khach_hang = relationship("KhachHang")

# 👤 Model Người Dùng - Hệ thống xác thực và phân quyền!
class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)  # 📧 Email đăng nhập
    ho_ten = Column(String(100), nullable=False)                          # 📛 Họ tên người dùng
    mat_khau_hash = Column(String(255), nullable=False)                   # 🔒 Mật khẩu đã hash
    vai_tro = Column(Enum(VaiTro), default=VaiTro.STAFF)                 # 🎭 Vai trò trong hệ thống
    is_active = Column(Boolean, default=True)                            # ✅ Tài khoản có hoạt động không
    ngay_tao = Column(DateTime, default=datetime.utcnow)                 # 📅 Ngày tạo tài khoản
    lan_dang_nhap_cuoi = Column(DateTime)                                # ⏰ Lần đăng nhập cuối
    so_dien_thoai = Column(String(20))                                   # 📱 Số điện thoại
    ghi_chu = Column(Text)                                               # 📝 Ghi chú về nhân viên

    # 🔗 Liên kết với các hoạt động (log activities)
    # activities = relationship("ActivityLog", back_populates="nguoi_dung")

# 📝 Audit Log - Ghi nhận hành động người dùng / hệ thống
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

# ⚙️ System Settings - Cấu hình hệ thống
class SystemSetting(Base):
    __tablename__ = "system_setting"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow)

# 🎯 Bùm! Xong phần models rồi!
# Giờ có thể tạo database và chơi với dữ liệu như một pro! 🚀
