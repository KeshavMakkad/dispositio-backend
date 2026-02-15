import csv
from pathlib import Path
from typing import IO, Sequence


def read_csv(
    file_path: str | Path | IO[str],
    *,
    encoding: str = "utf-8-sig",
    delimiter: str = ",",
    required_headers: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Read a CSV file and return its contents as a list of dictionaries."""

    def _read(handle: IO[str]) -> list[dict[str, str]]:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            raise ValueError("CSV file has no headers")
        if required_headers:
            missing = [h for h in required_headers if h not in reader.fieldnames]
            if missing:
                raise ValueError(f"Missing required headers: {', '.join(missing)}")

        rows: list[dict[str, str]] = []
        for row in reader:
            cleaned = {
                key: (value.strip() if isinstance(value, str) else "")
                for key, value in row.items()
                if key is not None
            }
            if any(value for value in cleaned.values()):
                rows.append(cleaned)
        return rows

    if hasattr(file_path, "read"):
        return _read(file_path)  # type: ignore[arg-type]

    with open(Path(file_path), "r", encoding=encoding, newline="") as handle:
        return _read(handle)