#!/usr/bin/env python3
"""
Basic FADO CRM Server - Minimal version that works
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("="*50)
    print("FADO CRM - BASIC SERVER")
    print("="*50)

    # Check if backend directory exists
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        return

    # Change to backend directory
    original_dir = os.getcwd()
    os.chdir(backend_dir)

    try:
        # Try to start a minimal FastAPI server
        print("Starting minimal FastAPI server...")

        # Create a minimal main.py if needed
        minimal_main = """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FADO CRM - Basic", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FADO CRM Basic Server is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "fado-crm-basic"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

        # Save minimal main.py
        with open("minimal_main.py", "w", encoding="utf-8") as f:
            f.write(minimal_main)

        # Start the server
        cmd = [sys.executable, "-m", "uvicorn", "minimal_main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        print("Command:", " ".join(cmd))
        print("\nStarting server...")
        print("Backend API will be at: http://localhost:8000")
        print("API Docs will be at: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the server")

        # Run the server
        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()