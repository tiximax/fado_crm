from database import SessionLocal
from models import NguoiDung
from auth import verify_password

from database import engine
print('DB URL:', engine.url)

db = SessionLocal()
try:
    user = db.query(NguoiDung).filter(NguoiDung.email=='admin@fado.vn').first()
    print('User found:', bool(user))
    if user:
        print('Hash:', user.mat_khau_hash[:30])
        ok = verify_password('admin123', user.mat_khau_hash)
        print('Verify admin123:', ok)
finally:
    db.close()
