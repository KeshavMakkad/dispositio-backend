from uuid import UUID

from db.enum import RoleEnum
from schemas.common import CamelCaseModel


class LoginRequest(CamelCaseModel):
    email: str


class AuthUserResponse(CamelCaseModel):
    id: UUID
    name: str
    email: str
    role: RoleEnum


class AuthResponse(CamelCaseModel):
    message: str
    user: AuthUserResponse


class MessageResponse(CamelCaseModel):
    message: str
