from datetime import datetime, timedelta
from jose import jwt
from auth import SECRET_KEY, ALGORITHM

payload = {
    "sub": "admin@fado.vn",
    "role": "admin",
    "type": "access",
    "exp": datetime.utcnow() + timedelta(minutes=30)
}
print(jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM))
