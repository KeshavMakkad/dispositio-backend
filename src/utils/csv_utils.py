import csv
import logging
from io import StringIO

logger = logging.getLogger(__name__)


def read_students_from_csv(content: bytes) -> list[str]:
    students = []

    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))

    if reader.fieldnames:
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

    logger.debug("csv parse start: bytes=%d headers=%s", len(content), reader.fieldnames)

    for row in reader:
        normalized_row = {str(k).strip().lower(): v for k, v in row.items()}
        email = normalized_row.get("email")
        if not email:
            # Fallback: accept single-column CSVs where the first column is email.
            values = [v for v in normalized_row.values() if v]
            email = values[0] if values else None
        if email:
            students.append(email.strip())

    logger.debug("csv parse complete: parsed_students=%d", len(students))

    return students
