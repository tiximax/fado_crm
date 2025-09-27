#!/usr/bin/env python3
# Simple FADO CRM Server - Skip complex package installation

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("\n" + "="*50)
    print("    FADO.VN CRM SYSTEM")
    print("="*50)
    print("API Backend: FastAPI + SQLAlchemy")
    print("Frontend: HTML + CSS + JavaScript")
    print("Features: Dashboard, CRM, Analytics")
    print("="*50)

def check_existing_packages():
    """Check if FastAPI is already installed"""
    try:
        import fastapi
        print("OK: FastAPI found")
        return True
    except ImportError:
        print("WARNING: FastAPI not found. Installing basic packages...")
        return False

def install_basic_packages():
    """Install only the most essential packages"""
    basic_packages = [
        "fastapi",
        "uvicorn[standard]",
        "python-multipart",
        "sqlalchemy",
        "python-dotenv"
    ]

    print("Installing basic packages...")
    for package in basic_packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"OK: {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"WARNING: Failed to install {package}: {e}")
            # Continue with other packages

    return True

def setup_database():
    """Setup database"""
    print("Setting up database...")

    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        return False

    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        sys.path.insert(0, '.')
        from database import create_tables
        create_tables()
        print("OK: Database setup complete!")
        return True
    except Exception as e:
        print(f"WARNING: Database setup failed: {str(e)}")
        print("Will try to continue without database setup...")
        return True  # Continue anyway
    finally:
        os.chdir(original_dir)

def start_backend():
    """Start the backend server"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        return None

    print("Starting backend server...")

    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        process = subprocess.Popen(cmd)
        print(f"OK: Backend server started with PID {process.pid}")
        print("Backend running at: http://localhost:8000")
        return process
    except Exception as e:
        print(f"ERROR: Failed to start backend: {str(e)}")
        return None
    finally:
        os.chdir(original_dir)

def start_frontend():
    """Start the frontend server"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("ERROR: Frontend directory not found!")
        return None

    print("Starting frontend server...")

    try:
        cmd = [sys.executable, "-m", "http.server", "8001", "--directory", str(frontend_dir)]
        process = subprocess.Popen(cmd)
        print(f"OK: Frontend server started with PID {process.pid}")
        print("Frontend running at: http://localhost:8001")
        return process
    except Exception as e:
        print(f"ERROR: Failed to start frontend: {str(e)}")
        return None

def main():
    """Main function"""
    print_banner()

    print("\nSystem Info:")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Directory: {os.getcwd()}")

    # Check if basic packages exist
    if not check_existing_packages():
        if not install_basic_packages():
            print("ERROR: Failed to install basic packages!")
            return

    # Setup database
    setup_database()

    # Start servers
    print("\n" + "="*50)
    print("STARTING SERVERS")
    print("="*50)

    backend_process = start_backend()
    if not backend_process:
        print("ERROR: Failed to start backend!")
        return

    frontend_process = start_frontend()
    if not frontend_process:
        print("ERROR: Failed to start frontend!")
        backend_process.terminate()
        return

    # Success
    print("\n" + "="*50)
    print("SUCCESS! FADO CRM IS RUNNING")
    print("="*50)
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:8001")
    print("API Docs: http://localhost:8000/docs")
    print("="*50)
    print("\nPress Ctrl+C to stop...")

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped!")

if __name__ == "__main__":
    main()