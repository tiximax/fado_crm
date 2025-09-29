from auth import verify_password
from database import SessionLocal, engine
from models import NguoiDung

print("DB URL:", engine.url)

db = SessionLocal()
try:
    user = db.query(NguoiDung).filter(NguoiDung.email == "admin@fado.vn").first()
    print("User found:", bool(user))
    if user:
        print("Hash:", (user.mat_khau_hash or "")[:30])
        ok = verify_password("admin123", user.mat_khau_hash)
        print("Verify admin123:", ok)
finally:
    db.close()
