import csv
from pathlib import Path

from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
import json

from core.exceptions import InternalServerErrorException
from services.seating import create_seating_service
from schemas.seating import (
    CreateSeatingRequest,
    SeatingListResponse,
    GetCapacityReqeust,
    create_seating_form,
)
from utils.csv_utils import read_students_from_csv

from db.models import Seating
from utils.db_utils import get_db_session
from uuid import UUID

router: APIRouter = APIRouter()


def _read_students_from_csv(file_path: Path) -> list[str]:
    students: list[str] = []
    with file_path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row.get("email")
            if email:
                students.append(email)
    return students


@router.post("/create")
async def create_seating(
    request: Request,
    student_list_one: UploadFile = File(...),
    student_list_two: UploadFile | None = File(None),
    args: CreateSeatingRequest = Depends(create_seating_form),
):

    # Parse CSV
    content_one = await student_list_one.read()
    args.student_list_one = read_students_from_csv(content_one)

    if student_list_two:
        content_two = await student_list_two.read()
        args.student_list_two = read_students_from_csv(content_two)

    return create_seating_service(request, args)


@router.get("/list")
def list_seating_arrangements(request: Request):
    with get_db_session(read_only=True) as session:
        seatings = session.query(Seating).all()
        return [
            SeatingListResponse(
                seating_id=seating.id,
                exam_name=seating.exam_name,
                exam_time=seating.exam_time,
            )
            for seating in seatings
        ]


@router.get("/{seating_id}")
def get_seating(request: Request, seating_id: str):
    """
    Temporarily generate seating arrangement from test CSVs.
    """
    id = seating_id

    with get_db_session(read_only=True) as session:
        seating = session.query(Seating).filter_by(id=id).first()
        if not seating:
            raise InternalServerErrorException("Seating arrangement not found.")
        return seating.seating_arrangement


@router.get("/capacity")
def get_capacity(request: Request, args: GetCapacityRequest):
    """
    Get the total capacity of all classrooms.
    """
