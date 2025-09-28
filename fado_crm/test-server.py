#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FADO CRM - Server Test Script
Quick test server without Docker
"""

import sys
import os
import asyncio
import threading
import time
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    import uvicorn
    from backend.main import app
    import requests
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install fastapi uvicorn requests")
    sys.exit(1)

def test_server():
    """Test server functionality"""
    print("🚀 FADO CRM Server Test")
    print("=" * 50)

    # Test app loading
    print("✅ App loaded successfully")
    print(f"📊 Routes available: {len(app.routes)}")

    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("backend/logs", exist_ok=True)

    print("📁 Created necessary directories")

    # Start server in background
    def run_server():
        uvicorn.run(
            "backend.main:app",
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False
        )

    print("🔄 Starting server on http://127.0.0.1:8000")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)

    # Test endpoints
    base_url = "http://127.0.0.1:8000"

    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")

        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
                print(f"   Response: {response.json()}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ Health endpoint not available")

        # Test dashboard endpoint
        try:
            response = requests.get(f"{base_url}/dashboard", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard endpoint working")
                dashboard_data = response.json()
                print(f"   Customers: {dashboard_data.get('tong_khach_hang', 'N/A')}")
                print(f"   Orders: {dashboard_data.get('tong_don_hang', 'N/A')}")
            else:
                print(f"❌ Dashboard endpoint failed: {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ Dashboard endpoint not available")

        # Test API docs
        try:
            response = requests.get(f"{base_url}/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API docs available")
            else:
                print(f"❌ API docs failed: {response.status_code}")
        except requests.exceptions.RequestException:
            print("⚠️ API docs not available")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

    print("\n🎉 Server test completed!")
    print("=" * 50)
    print("🌐 Access URLs:")
    print(f"   Frontend: {base_url}")
    print(f"   API Docs: {base_url}/docs")
    print(f"   Dashboard: {base_url}/dashboard")
    print("\n📚 Next steps:")
    print("   1. Open frontend/index.html in browser")
    print("   2. Check API docs for available endpoints")
    print("   3. Test with production Docker setup")

    return True

if __name__ == "__main__":
    try:
        success = test_server()
        if success:
            print("\n🔄 Server is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Server stopped.")
    except Exception as e:
        print(f"💥 Server test failed: {e}")
        sys.exit(1)