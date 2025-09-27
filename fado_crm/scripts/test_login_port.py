import requests, json, sys
base = sys.argv[1]
email = sys.argv[2]
pw = sys.argv[3]
r = requests.post(base.rstrip('/') + '/auth/login', json={'email': email, 'password': pw})
print(r.status_code)
try:
    print(json.dumps(r.json()))
except Exception:
    print(r.text)
