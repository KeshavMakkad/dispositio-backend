from schemas.common import CamelCaseModel


class ClassLayoutItem(CamelCaseModel):
    column_name: str
    column_capacity: str | int
    column_set: str


class AddClassRoomRequest(CamelCaseModel):
    name: str
    class_layout: list[ClassLayoutItem]
    columns_count: int
    max_rows: int
    capacity: int
