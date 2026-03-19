from uuid import UUID

from fastapi import APIRouter, Depends

from db.enum import RoleEnum
from db.models import User
from schemas.classroom import AddClassRoomRequest, ClassroomList, UpdateClassRoomRequest
from services.classroom import (
    create_classroom,
    deactivate_classroom,
    list_classrooms,
    update_classroom,
)
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


@router.put("/{classroom_id}")
def update_classroom_api(
    classroom_id: UUID,
    args: UpdateClassRoomRequest,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return update_classroom(classroom_id=classroom_id, args=args, actor_id=current_user.id)


@router.delete("/{classroom_id}")
def delete_classroom_api(
    classroom_id: UUID,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return deactivate_classroom(classroom_id=classroom_id, actor_id=current_user.id)
