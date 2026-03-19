from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File

from db.enum import RoleEnum
from db.models import User
from schemas.seating import (
    CreateSeatingRequest,
    GetCapacityRequest,
    SeatingListResponse,
    UpdateSeatingInfoRequest,
    UpdateSeatingPlanRequest,
    create_seating_form,
)
from services.seating import (
    create_seating_service,
    deactivate_seating,
    get_seating_by_id,
    get_seating_capacity,
    list_seatings,
    update_seating_info,
    update_seating_plan,
)
from utils.auth_dep import require_roles
from utils.csv_utils import read_students_from_csv

router: APIRouter = APIRouter()


@router.post("/create")
async def create_seating(
    student_list_one: UploadFile = File(...),
    student_list_two: UploadFile | None = File(None),
    args: CreateSeatingRequest = Depends(create_seating_form),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
):
    content_one = await student_list_one.read()
    args.student_list_one = read_students_from_csv(content_one)

    if student_list_two:
        content_two = await student_list_two.read()
        args.student_list_two = read_students_from_csv(content_two)

    return create_seating_service(args, actor_id=current_user.id)


@router.get("/list")
def list_seating_arrangements(
    _current_user: User = Depends(
        require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER)
    ),
) -> list[SeatingListResponse]:
    return list_seatings()


@router.get("/capacity")
def get_capacity(
    args: GetCapacityRequest = Depends(),
    _current_user: User = Depends(
        require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER)
    ),
) -> dict:
    return get_seating_capacity(args)


@router.get("/{seating_id}")
def get_seating(
    seating_id: UUID,
    _current_user: User = Depends(
        require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER)
    ),
) -> dict:
    return get_seating_by_id(seating_id)


@router.put("/{seating_id}/info")
def update_seating_info_api(
    seating_id: UUID,
    args: UpdateSeatingInfoRequest,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return update_seating_info(seating_id=seating_id, args=args, actor_id=current_user.id)


@router.put("/{seating_id}/plan")
def update_seating_plan_api(
    seating_id: UUID,
    args: UpdateSeatingPlanRequest,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return update_seating_plan(seating_id=seating_id, args=args, actor_id=current_user.id)


@router.delete("/{seating_id}")
def delete_seating_api(
    seating_id: UUID,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return deactivate_seating(seating_id=seating_id, actor_id=current_user.id)
