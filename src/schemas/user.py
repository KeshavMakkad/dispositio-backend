from db.enums import UserRoleEnum
from pydantic import EmailStr

from schemas.common import CamelCaseModel

class AddUserRequest(CamelCaseModel):
    name: str
    email: EmailStr
    role: UserRoleEnum