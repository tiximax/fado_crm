import json
import os  # Read token from generate_token.py from generate_token import jwt, SECRET_KEY, ALGORITHM, datetime, timedelta payload = { 'sub': 'admin@fado.vn', 'role': 'admin', 'type': 'access', 'exp': datetime.utcnow() + timedelta(minutes=30) } access = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) resp = requests.put( f'{backend}/admin/system-settings/app_name', headers={ 'Authorization': f'Bearer {access}' }, json={ 'value': 'FADO CRM PRO', 'description': 'Ten ung dung' } ) print(resp.status_code) print(resp.text)
import sys

import 'http://127.0.0.1:8000'
import =
import backend
import import
import requests
