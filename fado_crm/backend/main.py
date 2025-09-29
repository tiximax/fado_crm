# FADO CRM - Unified Main Entrypoint (Fixed)
# Mục tiêu: đảm bảo uvicorn --app-dir backend main:app chạy ổn định.
# Tạm thời ủy quyền app cho main_working.app (đầy đủ middleware, health, CRUD, auth).

# Hỗ trợ import linh hoạt cho cả chế độ chạy server và chạy pytest
try:
    from backend.app_full import app
except ModuleNotFoundError:
    from app_full import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
