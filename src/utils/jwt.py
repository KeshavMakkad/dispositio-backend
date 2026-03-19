from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt import InvalidTokenError

from core.config import settings
from core.exceptions import UnauthorizedException
from db.enum import RoleEnum

JWT_SECRET = settings.JWT_SECRET
ALGORITHM = "HS256"

ACCESS_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def _encode_token(payload: dict, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    token_payload = {
        **payload,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(token_payload, JWT_SECRET, algorithm=ALGORITHM)


def create_access_token(user_id: UUID, email: str, role: RoleEnum) -> str:
    return _encode_token(
        payload={
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "type": "access",
        },
        expires_delta=timedelta(minutes=ACCESS_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: UUID, email: str, role: RoleEnum) -> str:
    return _encode_token(
        payload={
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "type": "refresh",
        },
        expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS),
    )


def verify_token(token: str, expected_type: str | None = None) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except InvalidTokenError as exc:
        raise UnauthorizedException("Invalid or expired token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise UnauthorizedException("Invalid token type")

    return payload