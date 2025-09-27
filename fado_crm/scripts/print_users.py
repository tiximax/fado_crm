import sqlite3
conn = sqlite3.connect('fado_crm.db')
cur = conn.cursor()
for row in cur.execute('SELECT email, mat_khau_hash, vai_tro, is_active FROM nguoi_dung'):
    print('|'.join([str(x) for x in row]))
conn.close()
