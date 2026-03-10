from fastapi import APIRouter

from schemas.classroom import AddClassRoomRequest, ClassroomList
from services.classroom import create_classroom, list_classrooms

router: APIRouter = APIRouter()


@router.post("/add")
def add_classroom(args: AddClassRoomRequest) -> dict:
    return create_classroom(args)


@router.get("/list")
def get_classrooms() -> list[ClassroomList]:
    return list_classrooms()
