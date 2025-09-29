import json
import sys

import requests

email = sys.argv[1]
pw = sys.argv[2]
r = requests.post("http://127.0.0.1:8000/auth/login", json={"email": email, "password": pw})
print(r.status_code)
try:
    print(json.dumps(r.json()))
except Exception:
    print(r.text)
