from uuid import UUID

from pydantic import AliasChoices, Field, model_validator

from db.enum import RoleEnum
from schemas.common import CamelCaseModel


class LoginRequest(CamelCaseModel):
    supabase_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "supabaseToken", "supabase_token", "token", "accessToken"
        ),
    )
    email: str | None = None

    @model_validator(mode="after")
    def validate_login_payload(self) -> "LoginRequest":
        if not self.supabase_token and not self.email:
            raise ValueError("Either supabaseToken or email is required")
        return self


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
