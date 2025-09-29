#!/usr/bin/env python3
# FADO CRM Server Launcher - Simple ASCII version to avoid encoding issues

import os
import platform
import subprocess
import sys
from pathlib import Path


def print_banner():
    """Print startup banner"""
    banner = """
    FADO.VN CRM SYSTEM
    ====================================
    API Backend: FastAPI + SQLAlchemy
    Frontend: HTML + CSS + JavaScript
    Features: Dashboard, CRM, Analytics
    Built with AI Love & Vietnamese Spirit
    ====================================
    """
    print(banner)


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("ERROR: Need Python 3.8 or higher!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    else:
        print(f"OK: Python version: {sys.version}")


def check_virtual_environment():
    """Check virtual environment"""
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("OK: Running in virtual environment")
        return True
    else:
        print("WARNING: No virtual environment detected!")
        print("ADVICE: Create venv: python -m venv venv")
        return False


def install_requirements():
    """Install dependencies"""
    # Try minimal requirements first, then full requirements
    requirements_minimal = Path("backend/requirements_minimal.txt")
    requirements_file = Path("backend/requirements.txt")

    target_file = requirements_minimal if requirements_minimal.exists() else requirements_file

    if not target_file.exists():
        print("ERROR: No requirements file found!")
        return False

    print(f"Installing dependencies from {target_file.name}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(target_file)], check=True)
        print("OK: Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("ERROR: Failed to install dependencies!")
        # Try the minimal version if full version failed
        if target_file == requirements_file and requirements_minimal.exists():
            print("Trying minimal requirements...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(requirements_minimal)],
                    check=True,
                )
                print("OK: Minimal dependencies installed successfully!")
                return True
            except subprocess.CalledProcessError:
                print("ERROR: Failed to install even minimal dependencies!")
        return False


def setup_database():
    """Setup database"""
    print("Setting up database...")

    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        return False

    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        # Import and run database setup
        sys.path.insert(0, ".")
        from database import create_tables

        create_tables()
        print("OK: Database setup complete!")
        return True
    except Exception as e:
        print(f"ERROR: Database setup failed: {str(e)}")
        return False
    finally:
        os.chdir(original_dir)


def check_ports():
    """Check if required ports are available"""
    import socket

    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return True
            except OSError:
                return False

    ports_to_check = [8000, 8001]  # Backend and frontend ports

    for port in ports_to_check:
        if not is_port_available(port):
            print(f"WARNING: Port {port} is already in use!")
            return False

    print("OK: Required ports are available")
    return True


def start_backend():
    """Start the backend server"""
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        return False

    print("Starting backend server...")

    # Change to backend directory
    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        # Start uvicorn server
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload",
        ]
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
        return False

    print("Starting frontend server...")

    try:
        # Start simple HTTP server for frontend
        cmd = [sys.executable, "-m", "http.server", "8001", "--directory", str(frontend_dir)]
        process = subprocess.Popen(cmd)
        print(f"OK: Frontend server started with PID {process.pid}")
        print("Frontend running at: http://localhost:8001")
        return process
    except Exception as e:
        print(f"ERROR: Failed to start frontend: {str(e)}")
        return None


def show_system_info():
    """Display system information"""
    print("\n" + "=" * 50)
    print("SYSTEM INFORMATION")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Script Location: {__file__}")

    # Check if we're in the right directory
    required_dirs = ["backend", "frontend"]
    missing_dirs = [d for d in required_dirs if not Path(d).exists()]

    if missing_dirs:
        print(f"WARNING: Missing directories: {missing_dirs}")
    else:
        print("OK: All required directories found")


def main():
    """Main function to run the server"""
    try:
        print_banner()

        # System checks
        show_system_info()
        check_python_version()
        check_virtual_environment()

        # Database setup
        if not setup_database():
            print("ERROR: Database setup failed!")
            sys.exit(1)

        # Port availability check
        if not check_ports():
            print("WARNING: Some ports may be in use")

        # Install requirements
        print("\nInstalling/updating requirements...")
        if not install_requirements():
            print("ERROR: Failed to install requirements!")
            sys.exit(1)

        # Start servers
        print("\n" + "=" * 50)
        print("STARTING SERVERS")
        print("=" * 50)

        backend_process = start_backend()
        if not backend_process:
            print("ERROR: Failed to start backend server!")
            sys.exit(1)

        frontend_process = start_frontend()
        if not frontend_process:
            print("ERROR: Failed to start frontend server!")
            backend_process.terminate()
            sys.exit(1)

        # Success message
        print("\n" + "=" * 50)
        print("SUCCESS! FADO CRM IS RUNNING")
        print("=" * 50)
        print("Backend API: http://localhost:8000")
        print("Frontend UI: http://localhost:8001")
        print("API Docs: http://localhost:8000/docs")
        print("Admin Panel: http://localhost:8001/admin")
        print("=" * 50)
        print("\nPress Ctrl+C to stop the servers")

        # Keep the script running
        try:
            while True:
                import time

                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down servers...")
            backend_process.terminate()
            frontend_process.terminate()
            print("Servers stopped. Goodbye!")

    except Exception as e:
        print(f"FATAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
