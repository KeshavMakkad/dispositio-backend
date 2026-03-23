from datetime import datetime, timedelta, timezone
import json
from uuid import UUID

import jwt
import requests
from jwt.algorithms import ECAlgorithm, RSAAlgorithm
from jwt import InvalidTokenError

from core.config import settings
from core.exceptions import UnauthorizedException
from db.enum import RoleEnum

JWT_SECRET = settings.JWT_SECRET
SUPABASE_JWT_SECRET = settings.SUPABASE_JWT_SECRET or settings.JWT_SECRET
ALGORITHM = "HS256"

ACCESS_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def _decode_supabase_token_with_jwks(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    algorithm = header.get("alg")
    kid = header.get("kid")

    if not algorithm or not kid:
        raise InvalidTokenError("Supabase token missing alg or kid")

    unverified_payload = jwt.decode(
        token,
        options={"verify_signature": False, "verify_aud": False},
    )
    issuer = str(unverified_payload.get("iss") or "")
    if not issuer:
        raise InvalidTokenError("Supabase token missing issuer")

    # Expected issuer shape: https://<project>.supabase.co/auth/v1
    if "/auth/v1" in issuer:
        base_url = issuer.split("/auth/v1", 1)[0]
    else:
        base_url = issuer.rstrip("/")

    jwks_url = f"{base_url}/auth/v1/.well-known/jwks.json"
    response = requests.get(jwks_url, timeout=8)
    response.raise_for_status()
    keys = response.json().get("keys", [])

    matching_key = next((key for key in keys if key.get("kid") == kid), None)
    if not matching_key:
        raise InvalidTokenError("No matching JWKS key for Supabase token")

    if algorithm.startswith("ES"):
        public_key = ECAlgorithm.from_jwk(json.dumps(matching_key))
    elif algorithm.startswith("RS"):
        public_key = RSAAlgorithm.from_jwk(json.dumps(matching_key))
    else:
        raise InvalidTokenError(f"Unsupported Supabase token algorithm: {algorithm}")

    return jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
        options={"verify_aud": False},
    )


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


def get_email_from_supabase_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except InvalidTokenError as exc:
        try:
            payload = _decode_supabase_token_with_jwks(token)
        except (InvalidTokenError, requests.RequestException):
            raise UnauthorizedException(
                "Invalid or expired Supabase token. Verify Supabase project settings and token source."
            ) from exc

    email = payload.get("email")
    if not email:
        raise UnauthorizedException("Supabase token does not contain email")

    return str(email)