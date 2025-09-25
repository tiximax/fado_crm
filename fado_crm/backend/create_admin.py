# 👑 FADO CRM - Create First Admin User
# Script tạo tài khoản admin đầu tiên cho hệ thống! 🚀

import sys
import os
from getpass import getpass
from sqlalchemy.orm import Session

# Add current directory to path để import được các modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, create_tables
from models import NguoiDung, VaiTro
from auth import get_password_hash

def create_admin_user():
    """👑 Tạo tài khoản admin đầu tiên"""
    print("🚀 FADO CRM - Tạo tài khoản Admin đầu tiên")
    print("=" * 50)

    # Create database tables if not exist
    create_tables()

    db: Session = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(NguoiDung).filter(
            NguoiDung.vai_tro == VaiTro.ADMIN
        ).first()

        if existing_admin:
            print(f"⚠️  Admin user đã tồn tại: {existing_admin.email}")
            confirm = input("Bạn có muốn tạo admin user khác không? (y/n): ")
            if confirm.lower() != 'y':
                return

        # Get admin info
        print("\n📝 Nhập thông tin Admin:")
        email = input("📧 Email: ").strip()
        if not email:
            print("❌ Email không được để trống!")
            return

        # Check if email already exists
        existing_user = db.query(NguoiDung).filter(NguoiDung.email == email).first()
        if existing_user:
            print("❌ Email này đã được sử dụng!")
            return

        ho_ten = input("👤 Họ tên: ").strip()
        if not ho_ten:
            print("❌ Họ tên không được để trống!")
            return

        so_dien_thoai = input("📱 Số điện thoại (optional): ").strip()

        # Get password securely
        print("🔒 Nhập mật khẩu (tối thiểu 6 ký tự):")
        password = getpass("Mật khẩu: ")
        if len(password) < 6:
            print("❌ Mật khẩu phải có tối thiểu 6 ký tự!")
            return

        password_confirm = getpass("Xác nhận mật khẩu: ")
        if password != password_confirm:
            print("❌ Mật khẩu xác nhận không khớp!")
            return

        # Create admin user
        admin_user = NguoiDung(
            email=email,
            ho_ten=ho_ten,
            so_dien_thoai=so_dien_thoai if so_dien_thoai else None,
            mat_khau_hash=get_password_hash(password),
            vai_tro=VaiTro.ADMIN,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("\n🎉 Tạo tài khoản Admin thành công!")
        print(f"👤 Họ tên: {admin_user.ho_ten}")
        print(f"📧 Email: {admin_user.email}")
        print(f"🎭 Vai trò: {admin_user.vai_tro.value}")
        print(f"🆔 ID: {admin_user.id}")
        print("\n✅ Bạn có thể đăng nhập với thông tin này!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi tạo admin user: {str(e)}")

    finally:
        db.close()

def create_sample_users():
    """👥 Tạo một số user mẫu cho testing"""
    print("\n🎭 Tạo user mẫu cho testing...")

    db: Session = SessionLocal()

    sample_users = [
        {
            "email": "manager@fado.vn",
            "ho_ten": "Nguyễn Văn Manager",
            "password": "manager123",
            "vai_tro": VaiTro.MANAGER,
            "so_dien_thoai": "0901234567"
        },
        {
            "email": "staff@fado.vn",
            "ho_ten": "Trần Thị Staff",
            "password": "staff123",
            "vai_tro": VaiTro.STAFF,
            "so_dien_thoai": "0909876543"
        },
        {
            "email": "viewer@fado.vn",
            "ho_ten": "Lê Văn Viewer",
            "password": "viewer123",
            "vai_tro": VaiTro.VIEWER,
            "so_dien_thoai": "0908765432"
        }
    ]

    try:
        for user_data in sample_users:
            # Check if user already exists
            existing = db.query(NguoiDung).filter(NguoiDung.email == user_data["email"]).first()
            if existing:
                print(f"⚠️  User {user_data['email']} đã tồn tại")
                continue

            user = NguoiDung(
                email=user_data["email"],
                ho_ten=user_data["ho_ten"],
                so_dien_thoai=user_data["so_dien_thoai"],
                mat_khau_hash=get_password_hash(user_data["password"]),
                vai_tro=user_data["vai_tro"],
                is_active=True
            )

            db.add(user)
            print(f"✅ Tạo {user_data['vai_tro'].value}: {user_data['email']}")

        db.commit()
        print("🎉 Tạo user mẫu thành công!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi tạo user mẫu: {str(e)}")

    finally:
        db.close()

if __name__ == "__main__":
    try:
        create_admin_user()

        # Ask if user wants to create sample users
        create_samples = input("\n🎭 Bạn có muốn tạo user mẫu cho testing không? (y/n): ")
        if create_samples.lower() == 'y':
            create_sample_users()

        print("\n🚀 Script hoàn thành! Hệ thống sẵn sàng sử dụng!")

    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy bỏ!")
    except Exception as e:
        print(f"❌ Lỗi không mong đợi: {str(e)}")