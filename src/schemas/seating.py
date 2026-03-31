import json
from datetime import datetime
from uuid import UUID

from fastapi import Form

from schemas.classroom import ClassLayoutItem
from schemas.common import CamelCaseModel


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
    if not raw_classrooms:
        raise ValueError("classroomList is required")

    try:
        classrooms = json.loads(raw_classrooms)
    except json.JSONDecodeError:
        classrooms = [item.strip() for item in raw_classrooms.split(",") if item.strip()]

    return CreateSeatingRequest(
        student_list_one=[],
        student_list_two=None,
        classrooms_list=classrooms,
        exam_name=examName,
        exam_time=examTime,
    )
