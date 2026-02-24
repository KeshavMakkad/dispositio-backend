from collections.abc import Callable
from enum import EnumType
from functools import lru_cache
from db.models import User

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import UUID

from utils.datetime_utils import get_current_datetime


class IsActiveColumn:
    is_active = Column(
        Boolean, nullable=False, default=True, index=True, server_default=text("true")
    )


class TimestampColumn:
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=get_current_datetime,
        index=True,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=get_current_datetime,
        onupdate=get_current_datetime,
        server_default=func.now(),
    )


class AuditColumn:
    created_by = Column(
        "created_by",
        UUID(as_uuid=True),
        ForeignKey(User.id),
        nullable=False,
    )
    updated_by = Column(
        "updated_by",
        UUID(as_uuid=True),
        ForeignKey(User.id),
        nullable=False,
        index=True,
    )


class ChangeLogColumn:
    changes = Column("change_log", JSON, nullable=True)


__all__ = [
    "AuditColumn",
    "ChangeLogColumn",
    "IsActiveColumn",
    "TimestampColumn",
]
