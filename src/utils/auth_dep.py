from typing import Callable
from uuid import UUID

from fastapi import Depends, Request

from core.exceptions import ForbiddenException, UnauthorizedException
from db.enum import RoleEnum
from db.models import User
from repositories.user import UserRepository
from utils.db_utils import get_db_session
from utils.jwt import verify_token


def _get_cookie_token(request: Request, cookie_name: str) -> str:
    token = request.cookies.get(cookie_name)
    if not token:
        raise UnauthorizedException(f"Missing {cookie_name}")
    return token


def get_access_payload(request: Request) -> dict:
    token = _get_cookie_token(request, "access_token")
    return verify_token(token, expected_type="access")


def get_refresh_payload(request: Request) -> dict:
    token = _get_cookie_token(request, "refresh_token")
    return verify_token(token, expected_type="refresh")


def get_current_user(payload: dict = Depends(get_access_payload)) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token subject is missing")

    try:
        parsed_id = UUID(user_id)
    except ValueError as exc:
        raise UnauthorizedException("Invalid token subject") from exc

    with get_db_session(read_only=True) as session:
        repo = UserRepository(session)
        user = repo.get(parsed_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        return user


def get_user_from_refresh_payload(payload: dict = Depends(get_refresh_payload)) -> User:
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token subject is missing")

    try:
        parsed_id = UUID(user_id)
    except ValueError as exc:
        raise UnauthorizedException("Invalid token subject") from exc

    with get_db_session(read_only=True) as session:
        repo = UserRepository(session)
        user = repo.get(parsed_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        return user


def require_roles(*allowed_roles: RoleEnum) -> Callable[[User], User]:
    def _guard(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise ForbiddenException("You do not have permission to access this resource")
        return user

    return _guard