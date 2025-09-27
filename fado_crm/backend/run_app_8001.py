import sys
import uvicorn

# Force import from project backend directory, not any shadowed module
sys.path.insert(0, r"C:\Users\Admin\omnara-claude-20250923000733\fado_crm\backend")

import main as backend_main  # this should be C:\...\backend\main.py

if __name__ == "__main__":
    uvicorn.run(backend_main.app, host="127.0.0.1", port=8001)
