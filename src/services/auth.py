from datetime import timedelta

from fastapi import Response

from core.config import settings
from core.exceptions import UnauthorizedException
from db.models import User
from repositories.user import UserRepository
from schemas.auth import AuthResponse, AuthUserResponse, MessageResponse
from utils.db_utils import get_db_session
from utils.jwt import (
    create_access_token,
    create_refresh_token,
)


def _set_cookie(response: Response, key: str, value: str, max_age: int) -> None:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        max_age=max_age,
        path="/",
    )


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    _set_cookie(
        response=response,
        key="access_token",
        value=access_token,
        max_age=int(timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()),
    )
    _set_cookie(
        response=response,
        key="refresh_token",
        value=refresh_token,
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key="access_token",
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        domain=settings.COOKIE_DOMAIN,
    )


def _to_auth_user(user: User) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
    )


def login_user(email: str, response: Response) -> AuthResponse:
    with get_db_session(read_only=True) as session:
        repo = UserRepository(session)
        user = repo.get_by_email(email=email)

    if not user or not user.is_active:
        raise UnauthorizedException("User does not exist or is inactive")

    access_token = create_access_token(user.id, user.email, user.role)
    refresh_token = create_refresh_token(user.id, user.email, user.role)
    set_auth_cookies(response, access_token, refresh_token)

    return AuthResponse(message="Login successful", user=_to_auth_user(user))


def refresh_user_session(user: User, response: Response) -> AuthResponse:
    access_token = create_access_token(user.id, user.email, user.role)
    refresh_token = create_refresh_token(user.id, user.email, user.role)
    set_auth_cookies(response, access_token, refresh_token)

    return AuthResponse(message="Token refreshed", user=_to_auth_user(user))


def logout_user(response: Response) -> MessageResponse:
    clear_auth_cookies(response)
    return MessageResponse(message="Logout successful")
