from fastapi import APIRouter, Body, Depends, Header, Response

from core.exceptions import UnauthorizedException
from db.models import User
from schemas.auth import AuthResponse, AuthUserResponse, LoginRequest, MessageResponse
from services.auth import login_user, logout_user, refresh_user_session
from utils.auth_dep import get_current_user, get_user_from_refresh_payload

router: APIRouter = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(
    response: Response,
    args: LoginRequest | None = Body(default=None),
    authorization: str | None = Header(default=None),
) -> AuthResponse:
    bearer_token: str | None = None
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() == "bearer" and token:
            bearer_token = token

    body_token = args.supabase_token if args else None
    email = args.email if args else None
    resolved_token = body_token or bearer_token

    if not resolved_token and not email:
        raise UnauthorizedException("Missing login credentials")

    return login_user(
        response=response,
        supabase_token=resolved_token,
        email=email,
    )


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    response: Response,
    user: User = Depends(get_user_from_refresh_payload),
) -> AuthResponse:
    return refresh_user_session(user, response)


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response) -> MessageResponse:
    return logout_user(response)


@router.get("/me", response_model=AuthResponse)
def me(user: User = Depends(get_current_user)) -> AuthResponse:
    return AuthResponse(
        message="Current user fetched",
        user=AuthUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
        ),
    )
