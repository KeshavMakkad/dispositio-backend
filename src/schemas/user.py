from datetime import datetime
from uuid import UUID

from db.enum import RoleEnum
from schemas.common import CamelCaseModel


class CreateUserRequest(CamelCaseModel):
    name: str
    email: str
    role: RoleEnum


class UpdateUserRoleRequest(CamelCaseModel):
    role: RoleEnum


class UpdateUserRequest(CamelCaseModel):
    name: str
    email: str
    role: RoleEnum


class UserResponse(CamelCaseModel):
    id: UUID
    name: str
    email: str
    role: RoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime
