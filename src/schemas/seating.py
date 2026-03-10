from datetime import datetime

from uuid import UUID
from schemas.common import CamelCaseModel
from schemas.classroom import ClassLayoutItem
from fastapi import Form, Depends
import json


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


class GetSeatingRequest(CamelCaseModel):
    # seating_id: UUID
    pass


class SeatingListResponse(CamelCaseModel):
    seating_id: UUID
    exam_name: str
    exam_time: datetime


class GetCapacityReqeust(CamelCaseModel):
    classrooms_list: list[str]


def create_seating_form(
    classroomList: str = Form(...),
    examName: str = Form(...),
    examTime: datetime = Form(...),
):
    return CreateSeatingRequest(
        student_list_one=[],
        student_list_two=None,
        classrooms_list=json.loads(classroomList),
        exam_details=None,
        exam_name=examName,
        exam_time=examTime,
    )
