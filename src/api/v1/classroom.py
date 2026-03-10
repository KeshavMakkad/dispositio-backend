from fastapi import Request, APIRouter
from schemas.classroom import AddClassRoomRequest
from services.classroom import (
    create_classroom as create_classroom_service,
    list_classrooms_service,
)

router: APIRouter = APIRouter()


@router.post("/add")
async def create_classroom(request: Request, args: AddClassRoomRequest):
    """Call the service to create a new classroom."""
    return await create_classroom_service(request, args)


@router.get("/list")
async def list_classrooms(request: Request):
    """Call the service to list all classrooms."""
    return await list_classrooms_service(request)
