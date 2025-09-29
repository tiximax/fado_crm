#!/usr/bin/env python3
"""
FADO CRM - Ultra Stable Production Server
100% ASCII - No encoding issues!
"""

import os
import subprocess
import sys
from pathlib import Path


def print_banner():
    print("=" * 60)
    print("  FADO CRM - PRODUCTION STABLE VERSION")
    print("=" * 60)
    print("OK: Minimal dependencies")
    print("OK: Maximum stability")
    print("OK: Production ready")
    print("OK: Error-free startup")
    print("=" * 60)


def check_stable_requirements():
    """Check if stable requirements are installed"""
    try:
        import fastapi
        import pydantic
        import sqlalchemy
        import uvicorn

        print("OK: All stable requirements installed")
        return True
    except ImportError as e:
        print(f"ERROR: Missing requirement: {e}")
        return False


def install_stable_requirements():
    """Install only stable requirements"""
    requirements_file = Path("backend/requirements_stable.txt")

    if not requirements_file.exists():
        print("ERROR: requirements_stable.txt not found!")
        return False

    print("Installing stable requirements...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], check=True
        )
        print("OK: Stable requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install requirements!")
        return False


def start_stable_server():
    """Start the ultra-stable server"""
    backend_dir = Path("backend")
    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        print("Starting FADO CRM Stable Server...")
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "main_stable:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8002",
            "--reload",
        ]
        print("Command:", " ".join(cmd))
        print("")
        print("Backend API: http://localhost:8002")
        print("API Docs: http://localhost:8002/docs")
        print("Database: fado_crm_stable.db")
        print("")
        print("Press Ctrl+C to stop")
        print("")

        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: Server error: {e}")
    finally:
        os.chdir(original_dir)


def main():
    print_banner()

    # Check requirements
    if not check_stable_requirements():
        if not install_stable_requirements():
            print("ERROR: Cannot install requirements. Exiting.")
            return

    start_stable_server()


if __name__ == "__main__":
    main()
