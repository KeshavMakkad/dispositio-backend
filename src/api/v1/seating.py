import logging
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File

from db.enum import RoleEnum
from db.models import User
from schemas.seating import (
    CreateSeatingRequest,
    GetCapacityRequest,
    PrintStatusResponse,
    SeatingListResponse,
    StudentSeatingListResponse,
    UpdateSeatingInfoRequest,
    UpdateSeatingPlanRequest,
    create_seating_form,
)
from services.seating import (
    create_seating_service,
    deactivate_seating,
    get_seating_by_id,
    get_seating_capacity,
    get_seating_print_status,
    list_seatings_by_student_email,
    list_seatings,
    mark_seating_printed,
    update_seating_info,
    update_seating_plan,
)
from utils.auth_dep import get_optional_current_user, require_roles
from utils.csv_utils import read_students_from_csv
from core.exceptions import BadRequestException

router: APIRouter = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create")
async def create_seating(
    student_list_one: UploadFile | None = File(None),
    studentListOneFile: UploadFile | None = File(None),
    student_list_two: UploadFile | None = File(None),
    studentListTwoFile: UploadFile | None = File(None),
    args: CreateSeatingRequest = Depends(create_seating_form),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
):
    logger.debug(
        "create_seating request received: exam_name=%s exam_time=%s classrooms=%s file_fields_present={student_list_one:%s, studentListOneFile:%s, student_list_two:%s, studentListTwoFile:%s}",
        args.exam_name,
        args.exam_time,
        args.classrooms_list,
        bool(student_list_one),
        bool(studentListOneFile),
        bool(student_list_two),
        bool(studentListTwoFile),
    )

    file_one = student_list_one or studentListOneFile
    if not file_one:
        logger.debug("create_seating failed: primary student file missing")
        raise BadRequestException("student_list_one file is required")

    content_one = await file_one.read()
    args.student_list_one = read_students_from_csv(content_one)
    logger.debug(
        "primary student file parsed: filename=%s bytes=%d parsed_students=%d",
        file_one.filename,
        len(content_one),
        len(args.student_list_one),
    )

    file_two = student_list_two or studentListTwoFile
    if file_two:
        content_two = await file_two.read()
        args.student_list_two = read_students_from_csv(content_two)
        logger.debug(
            "secondary student file parsed: filename=%s bytes=%d parsed_students=%d",
            file_two.filename,
            len(content_two),
            len(args.student_list_two or []),
        )
    else:
        logger.debug("secondary student file not provided")

    logger.debug(
        "create_seating proceeding: set_one_count=%d set_two_count=%d",
        len(args.student_list_one),
        len(args.student_list_two or []),
    )

    return create_seating_service(args, actor_id=current_user.id)


@router.get("/list")
def list_seating_arrangements(
    _current_user: User = Depends(
        require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER)
    ),
) -> list[SeatingListResponse]:
    return list_seatings()


@router.get("/list/{email}")
def list_seating_arrangements_by_email(
    email: str,
) -> list[StudentSeatingListResponse]:
    return list_seatings_by_student_email(email)


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
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    return get_seating_by_id(
        seating_id,
        user_role=current_user.role if current_user else None,
    )


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


@router.get("/{seating_id}/print-status", response_model=PrintStatusResponse)
def get_print_status_api(
    seating_id: UUID,
    _current_user: User = Depends(
        require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN, RoleEnum.VIEWER)
    ),
) -> PrintStatusResponse:
    return get_seating_print_status(seating_id)


@router.post("/{seating_id}/print", response_model=PrintStatusResponse)
def mark_printed_api(
    seating_id: UUID,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> PrintStatusResponse:
    return mark_seating_printed(seating_id=seating_id, actor_id=current_user.id)


@router.delete("/{seating_id}")
def delete_seating_api(
    seating_id: UUID,
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.SUPER_ADMIN)),
) -> dict:
    return deactivate_seating(seating_id=seating_id, actor_id=current_user.id)
