from passlib.context import CryptContext
import sqlite3
ctx=CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')
conn=sqlite3.connect('fado_crm.db')
cur=conn.cursor()
h=cur.execute("SELECT mat_khau_hash FROM nguoi_dung WHERE email=?", ('manager@fado.vn',)).fetchone()[0]
print('verify:', ctx.verify('manager123', h))
conn.close()
