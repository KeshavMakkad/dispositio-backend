
from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    VIEWER = "viewer"