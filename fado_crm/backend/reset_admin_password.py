# Reset admin password to a new hash using current CryptContext
import sys, os
from database import SessionLocal, create_tables
from models import NguoiDung, VaiTro
from auth import get_password_hash

def main():
    create_tables()
    db = SessionLocal()
    try:
        user = db.query(NguoiDung).filter(NguoiDung.email == 'admin@fado.vn').first()
        if not user:
            print('Admin user not found, creating one...')
            user = NguoiDung(
                email='admin@fado.vn',
                ho_ten='FADO Admin',
                mat_khau_hash=get_password_hash('admin123'),
                vai_tro=VaiTro.ADMIN,
                is_active=True
            )
            db.add(user)
        else:
            user.mat_khau_hash = get_password_hash('admin123')
        db.commit()
        print('Admin password reset to admin123')
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == '__main__':
    main()
