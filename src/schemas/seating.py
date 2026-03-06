from uuid import UUID
from schemas.common import CamelCaseModel
from schemas.classroom import ClassLayoutItem

class ClassroomLayouts(CamelCaseModel):
    classroom_name: str
    layout: list[ClassLayoutItem]
    set_one_capacity: int
    set_two_capacity: int
    
class CreateSeatingRequest(CamelCaseModel):
    student_list_one: list[str]
    student_list_two: list[str]
    classrooms_list: list[str]
    classroom_details: list[ClassroomLayouts] | None = None

class GetSeatingRequest(CamelCaseModel):
    # seating_id: UUID
    pass