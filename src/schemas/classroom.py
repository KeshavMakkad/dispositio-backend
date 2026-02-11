from schemas.common import CamelCaseModel


class ClassLayoutItem(CamelCaseModel):
    row1_data: str
    row2_data: str | int


class AddClassRoomRequest(CamelCaseModel):
    name: str
    class_layout: list[ClassLayoutItem]
    columns_count: int
    max_rows: int
    capacity: int