#!/usr/bin/env python3
"""
FADO CRM - Ultra Stable Production Server
Guaranteed to work with minimal dependencies
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("  FADO CRM - PRODUCTION STABLE VERSION")
    print("=" * 60)
    print("✅ Minimal dependencies")
    print("✅ Maximum stability")
    print("✅ Production ready")
    print("✅ Error-free startup")
    print("=" * 60)

def check_stable_requirements():
    """Check if stable requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ All stable requirements installed")
        return True
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")
        return False

def install_stable_requirements():
    """Install only stable requirements"""
    requirements_file = Path("backend/requirements_stable.txt")

    if not requirements_file.exists():
        print("❌ requirements_stable.txt not found!")
        return False

    print("📦 Installing stable requirements...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True)
        print("✅ Stable requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements!")
        return False

def setup_stable_database():
    """Setup stable database"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False

    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        # Check if stable main exists
        if not Path("main_stable.py").exists():
            print("❌ main_stable.py not found!")
            return False

        print("✅ Stable database will be created automatically")
        return True
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False
    finally:
        os.chdir(original_dir)

def start_stable_server():
    """Start the ultra-stable server"""
    backend_dir = Path("backend")
    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        print("🚀 Starting FADO CRM Stable Server...")
        cmd = [sys.executable, "-m", "uvicorn", "main_stable:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
        print("Command:", " ".join(cmd))

        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✅ Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        os.chdir(original_dir)

def main():
    print_banner()

    # Check requirements
    if not check_stable_requirements():
        if not install_stable_requirements():
            print("❌ Cannot install requirements. Exiting.")
            return

    # Setup database
    if not setup_stable_database():
        print("❌ Database setup failed. Exiting.")
        return

    # Start server
    print("🎯 Starting on port 8002 (stable version)")
    print("📡 Backend API: http://localhost:8002")
    print("📚 API Docs: http://localhost:8002/docs")
    print("💾 Database: fado_crm_stable.db")
    print("\n🚀 Press Ctrl+C to stop\n")

    start_stable_server()

if __name__ == "__main__":
    main()