
from enum import Enum

from sqlalchemy import Enum as SQLAlchemyEnum


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    VIEWER = "VIEWER"


def role_enum_type(*, create_type: bool = True) -> SQLAlchemyEnum:
    """Return the SQLAlchemy enum type backed by RoleEnum.value entries."""
    return SQLAlchemyEnum(
        RoleEnum,
        name="role_enum",
        values_callable=lambda members: [member.value for member in members],
        create_type=create_type,
    )