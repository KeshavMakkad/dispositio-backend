from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File

from schemas.seating import (
    CreateSeatingRequest,
    GetCapacityRequest,
    SeatingListResponse,
    create_seating_form,
)
from services.seating import (
    create_seating_service,
    get_seating_by_id,
    get_seating_capacity,
    list_seatings,
)
from utils.csv_utils import read_students_from_csv

router: APIRouter = APIRouter()


@router.post("/create")
async def create_seating(
    student_list_one: UploadFile = File(...),
    student_list_two: UploadFile | None = File(None),
    args: CreateSeatingRequest = Depends(create_seating_form),
):
    content_one = await student_list_one.read()
    args.student_list_one = read_students_from_csv(content_one)

    if student_list_two:
        content_two = await student_list_two.read()
        args.student_list_two = read_students_from_csv(content_two)

    return create_seating_service(args)


@router.get("/list")
def list_seating_arrangements() -> list[SeatingListResponse]:
    return list_seatings()


@router.get("/capacity")
def get_capacity(args: GetCapacityRequest = Depends()) -> dict:
    return get_seating_capacity(args)


@router.get("/{seating_id}")
def get_seating(seating_id: UUID) -> dict:
    return get_seating_by_id(seating_id)
