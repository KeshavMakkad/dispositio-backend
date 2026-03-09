from sqlalchemy import UUID, Column, DateTime, String, JSON, Integer
from uuid import uuid4
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
    total_capacity = Column(Integer, nullable=False)
    set_one_capacity = Column(Integer, nullable=False, default=0)
    set_two_capacity = Column(Integer, nullable=False, default=0)

    __tablename__ = "classrooms"

class Seating(TimestampColumn, IsActiveColumn, AuditColumn, Base):
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    seating_arrangement = Column(JSON, nullable=False, default={})
    exam_name = Column(String(255), nullable=False)
    exam_time = Column(DateTime, nullable=False)
    __tablename__ = "seatings"
    