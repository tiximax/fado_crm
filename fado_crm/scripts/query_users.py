import json
import sqlite3

conn = sqlite3.connect("fado_crm.db")
cur = conn.cursor()
try:
    cur.execute("SELECT email, vai_tro, is_active FROM nguoidung")
    rows = cur.fetchall()
    print(json.dumps(rows))
except Exception as e:
    print("ERR:" + str(e))
finally:
    conn.close()
