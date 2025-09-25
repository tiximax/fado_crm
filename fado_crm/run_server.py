#!/usr/bin/env python3
# 🚀 FADO CRM Server Launcher - Khởi chạy như tên lửa!
# Script này sẽ khởi động server một cách ngầu và professional! ⚡

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """🎨 In banner siêu đẹp khi khởi động!"""
    banner = """
    🛍️  FADO.VN CRM SYSTEM  🛍️
    ════════════════════════════════════════
    🚀 API Backend: FastAPI + SQLAlchemy
    🎨 Frontend: HTML + CSS + JavaScript
    📊 Features: Dashboard, CRM, Analytics
    💖 Built with AI Love & Vietnamese Spirit
    ════════════════════════════════════════
    """
    print(banner)

def check_python_version():
    """🐍 Kiểm tra phiên bản Python"""
    if sys.version_info < (3, 8):
        print("❌ Cần Python 3.8 trở lên!")
        print(f"📍 Phiên bản hiện tại: {sys.version}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {sys.version}")

def check_virtual_environment():
    """🏠 Kiểm tra virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Đang chạy trong virtual environment")
        return True
    else:
        print("⚠️  Không phát hiện virtual environment!")
        print("💡 Khuyến nghị tạo venv: python -m venv venv")
        return False

def install_requirements():
    """📦 Cài đặt dependencies"""
    requirements_file = Path("backend/requirements.txt")

    if not requirements_file.exists():
        print("❌ Không tìm thấy requirements.txt!")
        return False

    print("📦 Cài đặt dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Cài đặt dependencies thành công!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Lỗi khi cài đặt dependencies!")
        return False

def setup_database():
    """🗄️ Thiết lập database"""
    print("🗄️ Thiết lập database...")

    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Không tìm thấy thư mục backend!")
        return False

    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        # Import và chạy database setup
        sys.path.insert(0, '.')
        from database import create_tables
        create_tables()
        print("✅ Database đã được thiết lập!")
        return True
    except Exception as e:
        print(f"❌ Lỗi thiết lập database: {e}")
        return False
    finally:
        os.chdir(original_dir)
        if '.' in sys.path:
            sys.path.remove('.')

def start_backend_server():
    """🖥️ Khởi động backend server"""
    print("🚀 Khởi động FastAPI backend server...")

    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Không tìm thấy thư mục backend!")
        return None

    try:
        # Chạy uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "."
        ]

        process = subprocess.Popen(
            cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        print("✅ Backend server đang chạy tại: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("📖 ReDoc: http://localhost:8000/redoc")

        return process

    except Exception as e:
        print(f"❌ Lỗi khởi động backend: {e}")
        return None

def open_frontend():
    """🌐 Mở frontend trong browser"""
    frontend_path = Path("frontend/index.html").absolute()

    if not frontend_path.exists():
        print("❌ Không tìm thấy file frontend/index.html!")
        return

    print("🌐 Mở frontend trong browser...")

    # Tạo URL file://
    frontend_url = f"file://{frontend_path}"

    try:
        system = platform.system().lower()
        if system == "windows":
            os.startfile(frontend_url)
        elif system == "darwin":  # macOS
            subprocess.run(["open", frontend_url])
        else:  # Linux
            subprocess.run(["xdg-open", frontend_url])

        print(f"✅ Frontend đã mở: {frontend_url}")
    except Exception as e:
        print(f"⚠️ Không thể mở browser tự động: {e}")
        print(f"💡 Mở thủ công: {frontend_url}")

def main():
    """🎯 Hàm chính - Main entry point"""
    print_banner()

    # 1. Kiểm tra Python version
    check_python_version()

    # 2. Kiểm tra virtual environment (optional warning)
    check_virtual_environment()

    # 3. Cài đặt dependencies
    print("\n📦 BƯỚC 1: Cài đặt dependencies...")
    if not install_requirements():
        print("❌ Dừng do lỗi cài đặt!")
        return

    # 4. Setup database
    print("\n🗄️ BƯỚC 2: Thiết lập database...")
    if not setup_database():
        print("❌ Dừng do lỗi database!")
        return

    # 5. Khởi động backend
    print("\n🚀 BƯỚC 3: Khởi động backend server...")
    backend_process = start_backend_server()

    if not backend_process:
        print("❌ Không thể khởi động backend!")
        return

    # 6. Mở frontend
    print("\n🌐 BƯỚC 4: Mở frontend...")
    open_frontend()

    # 7. Hướng dẫn sử dụng
    print("\n" + "="*50)
    print("🎉 FADO CRM ĐÃ SẴN SÀNG!")
    print("="*50)
    print("🖥️  Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🌐 Frontend: Đã mở trong browser")
    print("\n⌨️  Nhấn Ctrl+C để dừng server")
    print("="*50)

    try:
        # Đợi user dừng server
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Đang dừng server...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()

        print("✅ Server đã dừng!")
        print("👋 Cảm ơn bạn đã sử dụng FADO CRM!")

if __name__ == "__main__":
    main()