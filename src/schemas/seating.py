import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import Form

from schemas.classroom import ClassLayoutItem
from schemas.common import CamelCaseModel

logger = logging.getLogger(__name__)


class ClassroomLayouts(CamelCaseModel):
    classroom_name: str
    layout: list[ClassLayoutItem]
    set_one_capacity: int
    set_two_capacity: int


class CreateSeatingRequest(CamelCaseModel):
    student_list_one: list[str]
    student_list_two: list[str] | None = None
    classrooms_list: list[str]
    classroom_details: list[ClassroomLayouts] | None = None
    exam_name: str
    exam_time: datetime


class SeatingListResponse(CamelCaseModel):
    seating_id: UUID
    exam_name: str
    exam_time: datetime
    is_printed: bool = False
    printed_at: datetime | None = None
    # True when the plan was printed but has since been edited (printed copy is stale).
    needs_reprint: bool = False


class PrintStatusResponse(CamelCaseModel):
    seating_id: UUID
    is_printed: bool
    printed_at: datetime | None = None
    needs_reprint: bool = False


class StudentSeatingListResponse(CamelCaseModel):
    seating_id: UUID
    exam_name: str
    exam_time: datetime
    classrooms: list[str]


class UpdateSeatingInfoRequest(CamelCaseModel):
    exam_name: str
    exam_time: datetime


class UpdateSeatingPlanRequest(CamelCaseModel):
    seating_plan: dict


class GetCapacityRequest(CamelCaseModel):
    classrooms_list: list[str]


def create_seating_form(
    classroomList: str | None = Form(None),
    classroomsList: str | None = Form(None),
    examName: str = Form(...),
    examTime: datetime = Form(...),
) -> CreateSeatingRequest:
    raw_classrooms = classroomList or classroomsList
    logger.debug(
        "create_seating_form received: classroomList_present=%s classroomsList_present=%s examName=%s examTime=%s",
        classroomList is not None,
        classroomsList is not None,
        examName,
        examTime,
    )

    if not raw_classrooms:
        logger.debug("create_seating_form failed: classroom list field missing")
        raise ValueError("classroomList is required")

    try:
        classrooms = json.loads(raw_classrooms)
    except json.JSONDecodeError:
        classrooms = [item.strip() for item in raw_classrooms.split(",") if item.strip()]

    logger.debug("create_seating_form parsed classrooms_count=%d", len(classrooms))

    return CreateSeatingRequest(
        student_list_one=[],
        student_list_two=None,
        classrooms_list=classrooms,
        exam_name=examName,
        exam_time=examTime,
    )
