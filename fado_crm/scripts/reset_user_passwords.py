from passlib.context import CryptContext
import sqlite3

targets = {
    'manager@fado.vn': 'manager123',
    'staff@fado.vn': 'staff123',
    'viewer@fado.vn': 'viewer123',
}

conn = sqlite3.connect('fado_crm.db')
cur = conn.cursor()
updated = 0
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
for email, plain in targets.items():
    try:
        pwd_hash = pwd_context.hash(plain)
        cur.execute('UPDATE nguoi_dung SET mat_khau_hash = ? WHERE email = ?', (pwd_hash, email))
        updated += cur.rowcount
    except Exception as e:
        print(f'ERR updating {email}: {e}')
conn.commit()
print(f'updated={updated}')
conn.close()
