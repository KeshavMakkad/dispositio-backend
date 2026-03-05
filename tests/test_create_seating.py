import csv
import json
import os
import sys

# Add src directory to path so app imports resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from starlette.testclient import TestClient
from utils.app import app

client = TestClient(app)

TESTS_DIR = os.path.dirname(__file__)
STUDENTS_LIST_1_CSV = os.path.join(TESTS_DIR, "students_list_1.csv")
STUDENTS_LIST_2_CSV = os.path.join(TESTS_DIR, "students_list_2.csv")
DEBUG_OUTPUT_FILE = os.path.join(TESTS_DIR, "create_seating_debug.jsonl")

CREATE_SEATING_URL = "/api/v1/seating/seating/create"


def read_students_from_csv(filepath: str) -> list[str]:
    students = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append(row["email"])
    return students


def test_create_seating_with_default_layout():
    student_list_one = read_students_from_csv(STUDENTS_LIST_1_CSV)
    student_list_two = read_students_from_csv(STUDENTS_LIST_2_CSV)

    payload = {
        "studentListOne": student_list_one,
        "studentListTwo": student_list_two,
        "classroomsList": ["Classroom A"],
    }

    response = client.post(CREATE_SEATING_URL, json=payload)

    with open(DEBUG_OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(response.json()) + "\n")

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )

    data = response.json()
    assert "Classroom A" in data, (
        f"Expected 'Classroom A' key in response, got: {data}"
    )
