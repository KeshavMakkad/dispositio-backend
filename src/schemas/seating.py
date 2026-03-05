from schemas.common import CamelCaseModel
from schemas.classroom import ClassLayoutItem

class ClassroomLayouts(CamelCaseModel):
    classroom_name: str
    layout: list[ClassLayoutItem]
    set_one_capacity: int
    set_two_capacity: int
    
class CreateSeatingRequest(CamelCaseModel):
    student_list_one: list
    student_list_two: list
    classrooms_list: list
    classroom_details: list[ClassroomLayouts] | None = None