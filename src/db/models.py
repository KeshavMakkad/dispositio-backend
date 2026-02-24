from pydantic import EmailStr
from sqlalchemy import UUID, Column, String, JSON, Integer, Text
from uuid import uuid4
from db.enums import UserRoleEnum
from utils.models import (
    TimestampColumn,
    IsActiveColumn,
    AuditColumn
)
from core.db_core import Base

class Classroom(TimestampColumn, IsActiveColumn, AuditColumn, Base):
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    classroom_name = Column(String(255), nullable=False, unique=True)
    class_layout = Column(JSON, nullable=False, default={})
    columns_count = Column(Integer, nullable=False)
    max_rows = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False)
    
    __tablename__ = "classrooms"

class User(TimestampColumn, IsActiveColumn, Base):
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    role = Column(UserRoleEnum, nullable=False)
    __tablename__ = "users"