import csv
from pathlib import Path

from fastapi import APIRouter, Request

from core.exceptions import InternalServerErrorException
from services.seating import create_seating_service
from schemas.seating import CreateSeatingRequest

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

@router.post("/seating/create")
def create_seating(request: Request, args:CreateSeatingRequest):
    """
    Create a new seating arrangement.
    """
    return create_seating_service(request, args)


@router.get("/{seating_id}")
def get_seating(request: Request, seating_id: str):
    """
    Temporarily generate seating arrangement from test CSVs.
    """
    _ = seating_id

    project_root = Path(__file__).resolve().parents[3]
    tests_dir = project_root / "tests"

    student_list_one = _read_students_from_csv(tests_dir / "students_list_1.csv")
    student_list_two = _read_students_from_csv(tests_dir / "students_list_2.csv")

    if not student_list_one and not student_list_two:
        raise InternalServerErrorException("No students loaded from test CSV files.")

    args = CreateSeatingRequest(
        student_list_one=student_list_one,
        student_list_two=student_list_two,
        classrooms_list=["Classroom A"],
    )

    return create_seating_service(request, args)
