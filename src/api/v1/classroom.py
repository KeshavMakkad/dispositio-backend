from fastapi import APIRouter, Depends

from db.enum import RoleEnum
from db.models import User
from schemas.classroom import AddClassRoomRequest, ClassroomList
from services.classroom import create_classroom, list_classrooms
from utils.auth_dep import require_roles

router: APIRouter = APIRouter()


@router.post("/add")
def add_classroom(
    args: AddClassRoomRequest,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return create_classroom(args, actor_id=current_user.id)


@router.get("/list")
def get_classrooms(
    _current_user: User = Depends(
        require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER)
    ),
) -> list[ClassroomList]:
    return list_classrooms()
