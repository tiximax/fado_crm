import importlib.util
from pathlib import Path

import uvicorn

path = Path(r"C:\Users\Admin\omnara-claude-20250923000733\fado_crm\backend\main.py")

spec = importlib.util.spec_from_file_location("app_module", str(path))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if __name__ == "__main__":
    uvicorn.run(mod.app, host="127.0.0.1", port=8001)
