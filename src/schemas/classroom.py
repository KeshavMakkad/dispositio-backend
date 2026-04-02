from uuid import UUID

from schemas.common import CamelCaseModel


class ClassLayoutItem(CamelCaseModel):
    column_name: str
    column_capacity: str | int
    column_set: str


class ClassroomResponse(CamelCaseModel):
    classroom_id: UUID
    classroom_name: str
    class_layout: list[ClassLayoutItem]
    columns_count: int
    max_rows: int
    total_capacity: int
    set_1_capacity: int
    set_2_capacity: int


class AddClassRoomRequest(CamelCaseModel):
    name: str
    class_layout: list[ClassLayoutItem]
    columns_count: int
    max_rows: int
    total_capacity: int
    set_one_capacity: int
    set_two_capacity: int


class UpdateClassRoomRequest(CamelCaseModel):
    name: str
    class_layout: list[ClassLayoutItem]
    columns_count: int
    max_rows: int
    total_capacity: int
    set_one_capacity: int
    set_two_capacity: int


class SheetsUpsertClassroomsRequest(CamelCaseModel):
    classrooms: list[AddClassRoomRequest]


class SheetsUpsertClassroomsResponse(CamelCaseModel):
    message: str
    created_count: int
    updated_count: int
