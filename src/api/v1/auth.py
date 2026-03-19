from fastapi import APIRouter, Depends, Response

from db.models import User
from schemas.auth import AuthResponse, AuthUserResponse, LoginRequest, MessageResponse
from services.auth import login_user, logout_user, refresh_user_session
from utils.auth_dep import get_current_user, get_user_from_refresh_payload

router: APIRouter = APIRouter()


@router.post("/login", response_model=AuthResponse)
def login(args: LoginRequest, response: Response) -> AuthResponse:
    return login_user(args.email, response)


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
