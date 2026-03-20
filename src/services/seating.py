import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID

from core.config import settings
from core.constants import SYSTEM_USER_ID
from core.exceptions import BadRequestException, NotFoundException, TeapotException
from db.enum import RoleEnum
from db.models import Seating
from repositories.classroom import ClassroomRepository
from repositories.seating import SeatingRepository
from schemas.classroom import ClassLayoutItem
from schemas.seating import (
    ClassroomLayouts,
    CreateSeatingRequest,
    GetCapacityRequest,
    SeatingListResponse,
    StudentSeatingListResponse,
    UpdateSeatingInfoRequest,
    UpdateSeatingPlanRequest,
)
from services.classroom import get_default_class_details
from utils.db_utils import get_db_session


# ---------------------------------------------------------------------------
# Internal data structures
# ---------------------------------------------------------------------------


@dataclass
class ClassStudentAssignment:
    classroom_name: str
    layout: list[ClassLayoutItem]
    set_one_capacity: int
    set_two_capacity: int
    set_one_assigned_students: list[str] = field(default_factory=list)
    set_two_assigned_students: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _to_assignment(layout: ClassroomLayouts) -> ClassStudentAssignment:
    return ClassStudentAssignment(
        classroom_name=layout.classroom_name,
        layout=layout.layout,
        set_one_capacity=layout.set_one_capacity,
        set_two_capacity=layout.set_two_capacity,
    )


def _prepare_class_layouts(
    args: CreateSeatingRequest,
) -> dict[str, ClassStudentAssignment]:
    """Load layouts for each requested classroom (custom overrides first)."""
    custom_layouts = {
        detail.classroom_name: detail for detail in (args.classroom_details or [])
    }

    class_layouts: dict[str, ClassStudentAssignment] = {}
    for classroom in args.classrooms_list:
        source = custom_layouts.get(classroom) or get_default_class_details(classroom)
        class_layouts[classroom] = _to_assignment(source)

    return class_layouts


def _validate_capacity(
    args: CreateSeatingRequest,
    class_layouts: dict[str, ClassStudentAssignment],
) -> None:
    """Raise if classrooms lack capacity for the given student lists."""
    set_one_count = len(args.student_list_one)
    set_two_count = len(args.student_list_two or [])

    if set_one_count <= 0 and set_two_count <= 0:
        raise BadRequestException("No students to seat.")

    total_set_one_cap = sum(l.set_one_capacity for l in class_layouts.values())
    total_set_two_cap = sum(l.set_two_capacity for l in class_layouts.values())

    one_overflows = set_one_count > total_set_one_cap
    two_overflows = set_two_count > total_set_two_cap

    if (set_two_count == 0 and one_overflows) or (
        set_one_count == 0 and two_overflows
    ) or (one_overflows and two_overflows):
        raise BadRequestException("Total students exceed total classroom capacity.")


def _shuffle_students(
    args: CreateSeatingRequest,
) -> tuple[list[str], list[str]]:
    """Return shuffled copies of both student lists."""
    list_one = args.student_list_one.copy()
    list_two = (args.student_list_two or []).copy()
    random.shuffle(list_one)
    random.shuffle(list_two)
    return list_one, list_two


def _assign_students_to_classrooms(
    class_layouts: dict[str, ClassStudentAssignment],
    student_list_one: list[str],
    student_list_two: list[str],
) -> None:
    """Distribute students evenly across classrooms (mutates *class_layouts*)."""
    set_one_idx = 0
    set_two_idx = 0
    remaining_classes = len(class_layouts)

    for layout in class_layouts.values():
        remaining_one = len(student_list_one) - set_one_idx
        remaining_two = len(student_list_two) - set_two_idx

        if remaining_classes > 0:
            set_one_target = min(
                layout.set_one_capacity,
                (remaining_one + remaining_classes - 1) // remaining_classes,
            )
            set_two_target = min(
                layout.set_two_capacity,
                (remaining_two + remaining_classes - 1) // remaining_classes,
            )
        else:
            set_one_target = 0
            set_two_target = 0

        layout.set_one_assigned_students = student_list_one[
            set_one_idx : set_one_idx + set_one_target
        ]
        layout.set_two_assigned_students = student_list_two[
            set_two_idx : set_two_idx + set_two_target
        ]

        set_one_idx += set_one_target
        set_two_idx += set_two_target
        remaining_classes -= 1


def _generate_seating_for_classroom(
    layout: ClassStudentAssignment,
) -> list[list[str]]:
    """Build the 2-D seating grid (header + rows) for a single classroom."""
    columns = layout.layout
    header: list[str] = []
    capacities: list[int] = []

    for col in columns:
        if col.column_name == "-":
            header.append("-")
            capacities.append(0)
        else:
            header.append(col.column_name)
            try:
                capacities.append(int(col.column_capacity))
            except (TypeError, ValueError):
                capacities.append(0)

    rows: list[list[str]] = [header]
    max_rows = max(capacities) if capacities else 0

    for row_idx in range(max_rows):
        row: list[str] = []
        for col_idx, col in enumerate(columns):
            if col.column_name == "-":
                row.append("-")
            elif row_idx >= capacities[col_idx]:
                row.append("")
            elif col.column_set == "Set 1" and layout.set_one_assigned_students:
                row.append(layout.set_one_assigned_students.pop())
            elif col.column_set == "Set 2" and layout.set_two_assigned_students:
                row.append(layout.set_two_assigned_students.pop())
            else:
                row.append("")
        rows.append(row)

    return rows


def _generate_seating(
    class_layouts: dict[str, ClassStudentAssignment],
) -> dict[str, list[list[str]]]:
    return {
        name: _generate_seating_for_classroom(layout)
        for name, layout in class_layouts.items()
    }


# ---------------------------------------------------------------------------
# Public service functions (called by route handlers)
# ---------------------------------------------------------------------------


def create_seating_service(args: CreateSeatingRequest, actor_id: UUID = SYSTEM_USER_ID) -> dict:
    """Orchestrate the full seating-plan creation pipeline."""
    class_layouts = _prepare_class_layouts(args)
    _validate_capacity(args, class_layouts)

    set_one, set_two = _shuffle_students(args)
    _assign_students_to_classrooms(class_layouts, set_one, set_two)

    seating_plan = _generate_seating(class_layouts)

    with get_db_session(read_only=False) as session:
        repo = SeatingRepository(session)
        repo.create(
            Seating(
                seating_arrangement=seating_plan,
                exam_name=args.exam_name,
                exam_time=args.exam_time,
                created_by=actor_id,
                updated_by=actor_id,
            )
        )

    return {
        "message": "Seating arrangement created successfully.",
        "seating_plan": seating_plan,
    }


def get_seating_by_id(seating_id: UUID, user_role: RoleEnum | None = None) -> dict:
    """Fetch a single seating arrangement by its UUID."""
    with get_db_session(read_only=True) as session:
        repo = SeatingRepository(session)
        seating = repo.get_by_id(seating_id)
        if not seating:
            raise NotFoundException("Seating arrangement not found.")

        if user_role not in {RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN}:
            release_time = seating.exam_time - timedelta(
                minutes=settings.SEATING_VIEWER_ACCESS_TIME_DIFF_MINUTES
            )
            now = (
                datetime.now(tz=seating.exam_time.tzinfo)
                if seating.exam_time.tzinfo
                else datetime.utcnow()
            )
            if now < release_time:
                raise TeapotException("I am a teapot")

        return seating.seating_arrangement


def update_seating_info(
    seating_id: UUID,
    args: UpdateSeatingInfoRequest,
    actor_id: UUID = SYSTEM_USER_ID,
) -> dict:
    with get_db_session(read_only=False) as session:
        repo = SeatingRepository(session)
        seating = repo.get_by_id(seating_id)
        if not seating:
            raise NotFoundException("Seating arrangement not found.")

        updated = repo.update(
            seating_id,
            exam_name=args.exam_name,
            exam_time=args.exam_time,
            updated_by=actor_id,
        )

    if not updated:
        raise NotFoundException("Seating arrangement not found.")

    return {"message": "Seating info updated successfully."}


def update_seating_plan(
    seating_id: UUID,
    args: UpdateSeatingPlanRequest,
    actor_id: UUID = SYSTEM_USER_ID,
) -> dict:
    with get_db_session(read_only=False) as session:
        repo = SeatingRepository(session)
        seating = repo.get_by_id(seating_id)
        if not seating:
            raise NotFoundException("Seating arrangement not found.")

        updated = repo.update(
            seating_id,
            seating_arrangement=args.seating_plan,
            updated_by=actor_id,
        )

    if not updated:
        raise NotFoundException("Seating arrangement not found.")

    return {"message": "Seating plan updated successfully."}


def deactivate_seating(seating_id: UUID, actor_id: UUID = SYSTEM_USER_ID) -> dict:
    with get_db_session(read_only=False) as session:
        repo = SeatingRepository(session)
        seating = repo.get_by_id(seating_id)
        if not seating:
            raise NotFoundException("Seating arrangement not found.")

        repo.update(seating_id, is_active=False, updated_by=actor_id)

    return {"message": "Seating deleted successfully."}


def list_seatings() -> list[SeatingListResponse]:
    """Return summary info for every seating arrangement."""
    with get_db_session(read_only=True) as session:
        repo = SeatingRepository(session)
        seatings = repo.get_all_active()
        return [
            SeatingListResponse(
                seating_id=s.id,
                exam_name=s.exam_name,
                exam_time=s.exam_time,
            )
            for s in seatings
        ]


def list_seatings_by_student_email(email: str) -> list[StudentSeatingListResponse]:
    """Return seating summaries where the given student email appears."""
    target_email = email.strip().lower()
    if not target_email:
        raise BadRequestException("Email is required")

    matches: list[StudentSeatingListResponse] = []
    with get_db_session(read_only=True) as session:
        repo = SeatingRepository(session)
        seatings = repo.get_all_active()

        for seating in seatings:
            arrangement = seating.seating_arrangement or {}
            matched_classrooms: list[str] = []

            for classroom_name, rows in arrangement.items():
                classroom_has_student = False
                for row in rows:
                    for cell in row:
                        if isinstance(cell, str) and cell.strip().lower() == target_email:
                            classroom_has_student = True
                            break
                    if classroom_has_student:
                        break

                if classroom_has_student:
                    matched_classrooms.append(classroom_name)

            if matched_classrooms:
                matches.append(
                    StudentSeatingListResponse(
                        seating_id=seating.id,
                        exam_name=seating.exam_name,
                        exam_time=seating.exam_time,
                        classrooms=matched_classrooms,
                    )
                )

    return matches


def get_seating_capacity(args: GetCapacityRequest) -> dict:
    """Aggregate set-one / set-two capacity across requested classrooms."""
    set_one_capacity = 0
    set_two_capacity = 0

    for classroom in args.classrooms_list:
        details = get_default_class_details(classroom)
        set_one_capacity += details.set_one_capacity
        set_two_capacity += details.set_two_capacity

    return {
        "total_capacity": set_one_capacity + set_two_capacity,
        "set_one_capacity": set_one_capacity,
        "set_two_capacity": set_two_capacity,
    }
