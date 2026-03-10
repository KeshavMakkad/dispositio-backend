from schemas.common import CamelCaseModel


class ClassLayoutItem(CamelCaseModel):
    column_name: str
    column_capacity: str | int
    column_set: str


class ClassroomList(CamelCaseModel):
    classroom_name: str


class AddClassRoomRequest(CamelCaseModel):
    name: str
    class_layout: list[ClassLayoutItem]
    columns_count: int
    max_rows: int
    total_capacity: int
    set_one_capacity: int
    set_two_capacity: int
