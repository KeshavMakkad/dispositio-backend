from uuid import UUID

from fastapi import APIRouter, Depends

from db.enum import RoleEnum
from db.models import User
from schemas.classroom import (
    AddClassRoomRequest,
    ClassroomResponse,
    SheetsUpsertClassroomsRequest,
    SheetsUpsertClassroomsResponse,
    UpdateClassRoomRequest,
)
from services.classroom import (
    create_classroom,
    deactivate_classroom,
    list_classrooms,
    upsert_classrooms_from_sheets,
    update_classroom,
)
from utils.auth_dep import require_roles, require_sheets_api_key

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
) -> list[ClassroomResponse]:
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


@router.post(
    "/sheets/upsert",
    response_model=SheetsUpsertClassroomsResponse,
    dependencies=[Depends(require_sheets_api_key)],
)
def upsert_classrooms_from_google_sheets(
    args: SheetsUpsertClassroomsRequest,
) -> SheetsUpsertClassroomsResponse:
    return upsert_classrooms_from_sheets(args.classrooms)
