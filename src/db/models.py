from uuid import uuid4

from sqlalchemy import UUID, Boolean, Column, DateTime, Integer, JSON, String, text

from core.db_core import Base
from utils.models import AuditColumn, IsActiveColumn, TimestampColumn
from db.enum import RoleEnum, role_enum_type


class Classroom(TimestampColumn, IsActiveColumn, AuditColumn, Base):
    __tablename__ = "classrooms"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    classroom_name = Column(String(255), nullable=False, unique=True)
    class_layout = Column(JSON, nullable=False, default=dict)
    columns_count = Column(Integer, nullable=False)
    max_rows = Column(Integer, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    set_one_capacity = Column(Integer, nullable=False, default=0)
    set_two_capacity = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Classroom {self.classroom_name!r}>"


class Seating(TimestampColumn, IsActiveColumn, AuditColumn, Base):
    __tablename__ = "seatings"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    seating_arrangement = Column(JSON, nullable=False, default=dict)
    exam_name = Column(String(255), nullable=False)
    exam_time = Column(DateTime, nullable=False)
    # Print tracking: is_printed flips to False whenever the plan is edited
    # after being printed; printed_at preserves when it was last printed so the
    # frontend can warn that a printed plan has since changed.
    is_printed = Column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    printed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Seating {self.exam_name!r} id={self.id}>"

class User(TimestampColumn, IsActiveColumn, AuditColumn, Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    name = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(role_enum_type(), nullable=False, default=RoleEnum.VIEWER)

    def __repr__(self) -> str:
        return f"<User {self.name!r} id={self.id}>"