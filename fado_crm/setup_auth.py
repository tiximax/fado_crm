# 🚀 FADO CRM - Setup Authentication System
# Script setup hệ thống xác thực Phase 2! 🔐

import os
import sys
import subprocess

def main():
    print("🚀 FADO CRM - Setup Authentication System Phase 2")
    print("=" * 60)

    # Install additional dependencies
    print("📦 Cài đặt dependencies bổ sung...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-jose[cryptography]==3.3.0"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "passlib[bcrypt]==1.7.4"])
        print("✅ Dependencies đã được cài đặt!")
    except subprocess.CalledProcessError:
        print("⚠️  Dependencies có thể đã được cài đặt từ trước")

    # Navigate to backend directory
    backend_path = os.path.join(os.getcwd(), "backend")
    if not os.path.exists(backend_path):
        print(f"❌ Không tìm thấy thư mục backend: {backend_path}")
        return

    os.chdir(backend_path)
    print(f"📂 Chuyển đến thư mục: {backend_path}")

    # Create database tables (including new user table)
    print("🗄️  Tạo database tables...")
    try:
        import sys
        sys.path.append(os.getcwd())
        from database import create_tables
        create_tables()
        print("✅ Database tables đã được tạo!")
    except Exception as e:
        print(f"⚠️  Lỗi tạo database: {str(e)}")

    # Create admin user
    print("\n👑 Tạo tài khoản Admin đầu tiên...")
    try:
        subprocess.check_call([sys.executable, "create_admin.py"])
    except subprocess.CalledProcessError:
        print("⚠️  Có thể admin user đã tồn tại")

    # Start server
    print("\n🚀 Khởi động server...")
    print("📝 Các tính năng mới trong Phase 2:")
    print("   🔐 JWT Authentication")
    print("   🎭 Role-based Access Control (RBAC)")
    print("   👑 Admin: Toàn quyền")
    print("   👨‍💼 Manager: Quản lý khách hàng, sản phẩm")
    print("   👨‍💻 Staff: Xem và tạo đơn hàng")
    print("   👁️  Viewer: Chỉ xem")
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("🔐 Authentication endpoints:")
    print("   POST /auth/login - Đăng nhập")
    print("   POST /auth/refresh - Refresh token")
    print("   GET /auth/me - Thông tin user hiện tại")
    print("   POST /auth/change-password - Đổi mật khẩu")
    print("   GET /users/ - Danh sách users (Admin only)")
    print("   POST /users/ - Tạo user mới (Admin only)")

    try:
        print("\n⚡ Starting server...")
        subprocess.check_call([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n👋 Server đã dừng!")
    except Exception as e:
        print(f"❌ Lỗi khởi động server: {str(e)}")

if __name__ == "__main__":
    main()