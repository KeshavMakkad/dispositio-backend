from uuid import UUID

from fastapi import APIRouter, Depends

from db.enum import RoleEnum
from db.models import User
from schemas.user import CreateUserRequest, UpdateUserRoleRequest, UserResponse
from services.user import create_user, deactivate_user, list_users, update_user_role
from utils.auth_dep import require_roles

router: APIRouter = APIRouter(
    dependencies=[Depends(require_roles(RoleEnum.SUPER_ADMIN))]
)


@router.post("/create", response_model=UserResponse)
def create_user_api(
    args: CreateUserRequest,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> UserResponse:
    return create_user(args, actor_id=current_user.id)


@router.get("/list", response_model=list[UserResponse])
def list_users_api() -> list[UserResponse]:
    return list_users()


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role_api(
    user_id: UUID,
    args: UpdateUserRoleRequest,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> UserResponse:
    return update_user_role(user_id=user_id, args=args, actor_id=current_user.id)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user_api(
    user_id: UUID,
    current_user: User = Depends(require_roles(RoleEnum.SUPER_ADMIN)),
) -> UserResponse:
    return deactivate_user(user_id=user_id, actor_id=current_user.id)
