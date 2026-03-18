import jwt
from datetime import datetime, timedelta

from core.config import settings

JWT_SECRET = settings.SUPABASE_JWT_SECRET
ALGORITHM = "HS256"

ACCESS_EXPIRE_MINUTES = 15
REFRESH_EXPIRE_DAYS = 7


def create_access_token(admin_id: str):
    payload = {
        "sub": admin_id,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(admin_id: str):
    payload = {
        "sub": admin_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def verify_token(token: str):
    print('*' * 100)
    print(token)
    print('*' *100)
    token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    return token