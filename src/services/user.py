from uuid import UUID

from core.exceptions import BadRequestException, NotFoundException
from db.enum import RoleEnum
from db.models import User
from repositories.user import UserRepository
from schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UpdateUserRoleRequest,
    UserResponse,
)
from utils.db_utils import get_db_session


def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def create_user(args: CreateUserRequest, actor_id: UUID) -> UserResponse:
    if args.role not in {RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER}:
        raise BadRequestException("Invalid role")

    with get_db_session(read_only=False) as session:
        repo = UserRepository(session)
        if repo.get_by_email(args.email):
            raise BadRequestException("User with this email already exists")

        existing_name = repo.filter(name=args.name)
        if existing_name:
            raise BadRequestException("User with this name already exists")

        user = repo.create(
            User(
                name=args.name,
                email=args.email,
                role=args.role,
                is_active=True,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )

    return _to_user_response(user)


def list_users() -> list[UserResponse]:
    with get_db_session(read_only=True) as session:
        repo = UserRepository(session)
        users = repo.list_users()

    return [_to_user_response(user) for user in users]


def update_user_role(user_id: UUID, args: UpdateUserRoleRequest, actor_id: UUID) -> UserResponse:
    with get_db_session(read_only=False) as session:
        repo = UserRepository(session)
        user = repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")

        updated = repo.update(user_id, role=args.role, updated_by=actor_id)

    if not updated:
        raise NotFoundException("User not found")

    return _to_user_response(updated)


def deactivate_user(user_id: UUID, actor_id: UUID) -> UserResponse:
    with get_db_session(read_only=False) as session:
        repo = UserRepository(session)
        user = repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")

        if not user.is_active:
            return _to_user_response(user)

        updated = repo.deactivate_user(user_id=user_id, updated_by=actor_id)

    if not updated:
        raise NotFoundException("User not found")

    return _to_user_response(updated)


def update_user(user_id: UUID, args: UpdateUserRequest, actor_id: UUID) -> UserResponse:
    with get_db_session(read_only=False) as session:
        repo = UserRepository(session)
        user = repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")

        duplicate_email = repo.get_by_email(args.email)
        if duplicate_email and duplicate_email.id != user_id:
            raise BadRequestException("User with this email already exists")

        duplicate_name = repo.filter(name=args.name)
        if any(u.id != user_id for u in duplicate_name):
            raise BadRequestException("User with this name already exists")

        updated = repo.update(
            user_id,
            name=args.name,
            email=args.email,
            role=args.role,
            updated_by=actor_id,
        )

    if not updated:
        raise NotFoundException("User not found")

    return _to_user_response(updated)


def delete_user(user_id: UUID, actor_id: UUID) -> UserResponse:
    return deactivate_user(user_id=user_id, actor_id=actor_id)
