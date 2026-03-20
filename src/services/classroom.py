from uuid import UUID

from core.constants import SYSTEM_USER_ID
from core.exceptions import BadRequestException, NotFoundException
from db.models import Classroom
from repositories.classroom import ClassroomRepository
from schemas.classroom import AddClassRoomRequest, ClassroomList, UpdateClassRoomRequest
from schemas.seating import ClassroomLayouts
from utils.db_utils import get_db_session


def get_default_class_details(class_name: str) -> ClassroomLayouts:
    """Return layout metadata for *class_name*, or raise 400 if unknown."""
    with get_db_session(read_only=True) as session:
        repo = ClassroomRepository(session)
        classroom = repo.get_by_name(class_name)
        if not classroom:
            raise BadRequestException(f"Classroom '{class_name}' not found.")

        return ClassroomLayouts(
            classroom_name=classroom.classroom_name,
            layout=classroom.class_layout,
            set_one_capacity=classroom.set_one_capacity,
            set_two_capacity=classroom.set_two_capacity,
        )


def create_classroom(args: AddClassRoomRequest, actor_id: UUID = SYSTEM_USER_ID) -> dict:
    """Persist a new classroom, rejecting duplicates."""
    with get_db_session(read_only=False) as session:
        repo = ClassroomRepository(session)
        if repo.get_by_name(args.name):
            raise BadRequestException("Classroom with this name already exists.")

        class_layout_data = [item.model_dump() for item in args.class_layout]
        repo.create(
            Classroom(
                classroom_name=args.name,
                class_layout=class_layout_data,
                columns_count=args.columns_count,
                max_rows=args.max_rows,
                total_capacity=args.total_capacity,
                set_one_capacity=args.set_one_capacity,
                set_two_capacity=args.set_two_capacity,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )

    return {"message": "Classroom created successfully."}


def update_classroom(
    classroom_id: UUID,
    args: UpdateClassRoomRequest,
    actor_id: UUID = SYSTEM_USER_ID,
) -> dict:
    with get_db_session(read_only=False) as session:
        repo = ClassroomRepository(session)
        classroom = repo.get_by_id(classroom_id)
        if not classroom:
            raise NotFoundException("Classroom not found")

        duplicate = repo.get_by_name(args.name)
        if duplicate and duplicate.id != classroom_id:
            raise BadRequestException("Classroom with this name already exists.")

        class_layout_data = [item.model_dump() for item in args.class_layout]
        updated = repo.update(
            classroom_id,
            classroom_name=args.name,
            class_layout=class_layout_data,
            columns_count=args.columns_count,
            max_rows=args.max_rows,
            total_capacity=args.total_capacity,
            set_one_capacity=args.set_one_capacity,
            set_two_capacity=args.set_two_capacity,
            updated_by=actor_id,
        )

    if not updated:
        raise NotFoundException("Classroom not found")

    return {"message": "Classroom updated successfully."}


def deactivate_classroom(classroom_id: UUID, actor_id: UUID = SYSTEM_USER_ID) -> dict:
    with get_db_session(read_only=False) as session:
        repo = ClassroomRepository(session)
        classroom = repo.get_by_id(classroom_id)
        if not classroom:
            raise NotFoundException("Classroom not found")

        repo.update(classroom_id, is_active=False, updated_by=actor_id)

    return {"message": "Classroom deleted successfully."}


def list_classrooms() -> list[ClassroomList]:
    """Return the name of every classroom."""
    with get_db_session(read_only=True) as session:
        repo = ClassroomRepository(session)
        classrooms = repo.list_active()
        return [
            ClassroomList(
                classroom_name=c.classroom_name,
                set_1_capacity=c.set_one_capacity,
                set_2_capacity=c.set_two_capacity,
                total_capacity=c.total_capacity
            ) for c in classrooms
        ]
