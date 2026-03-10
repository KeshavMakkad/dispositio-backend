import csv
from io import StringIO


def read_students_from_csv(content: bytes) -> list[str]:
    students = []

    text = content.decode("utf-8")
    reader = csv.DictReader(StringIO(text))

    for row in reader:
        email = row.get("email")
        if email:
            students.append(email)

    return students
