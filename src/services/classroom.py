from fastapi import Request
from uuid import UUID

from core.exceptions import BadRequestException
from db.models import Classroom
from schemas.classroom import AddClassRoomRequest, ClassroomList
from schemas.seating import ClassroomLayouts
from utils.db_utils import get_db_session

# Dummy UUID for system operations (to be replaced later)
SYSTEM_USER_ID = UUID("00000000-0000-0000-0000-000000000000")


def get_default_class_details(class_name: str):
    """
    Get the details of a specific class.
    """
    with get_db_session(read_only=True) as session:
        classroom = (
            session.query(Classroom).filter_by(classroom_name=class_name).first()
        )
        if not classroom:
            raise BadRequestException("Classroom not found.")

        return ClassroomLayouts(
            classroom_name=classroom.classroom_name,
            layout=classroom.class_layout,
            set_one_capacity=classroom.set_one_capacity,
            set_two_capacity=classroom.set_two_capacity,
        )


async def create_classroom(request: Request, args: AddClassRoomRequest):
    with get_db_session(read_only=False) as session:
        existing_classroom = (
            session.query(Classroom).filter_by(classroom_name=args.name).first()
        )
        if existing_classroom:
            raise BadRequestException("Classroom with this name already exists.")

        # Convert Pydantic models to dictionaries for JSON serialization
        class_layout_data = [item.model_dump() for item in args.class_layout]

        new_classroom = Classroom(
            classroom_name=args.name,
            class_layout=class_layout_data,
            columns_count=args.columns_count,
            max_rows=args.max_rows,
            total_capacity=args.total_capacity,
            set_one_capacity=args.set_one_capacity,
            set_two_capacity=args.set_two_capacity,
            updated_by=SYSTEM_USER_ID,
            created_by=SYSTEM_USER_ID,
        )
        session.add(new_classroom)

    return {"message": "Classroom created successfully."}


async def list_classrooms_service(request: Request):
    with get_db_session(read_only=True) as session:
        classrooms = session.query(Classroom).all()
        return [
            ClassroomList(
                classroom_name=classroom.classroom_name,
            )
            for classroom in classrooms
        ]
