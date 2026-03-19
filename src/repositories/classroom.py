from uuid import UUID

from sqlalchemy.orm import Session

from db.base import BaseRepository
from db.models import Classroom


class ClassroomRepository(BaseRepository[Classroom]):
    def __init__(self, db: Session):
        super().__init__(Classroom, db)

    def get_by_name(self, name: str, include_inactive: bool = False) -> Classroom | None:
        filters = {"classroom_name": name}
        if not include_inactive:
            filters["is_active"] = True
        results = self.filter(**filters)
        return results[0] if results else None

    def get_by_id(self, classroom_id: UUID, include_inactive: bool = False) -> Classroom | None:
        if include_inactive:
            return self.get(classroom_id)
        results = self.filter(id=classroom_id, is_active=True)
        return results[0] if results else None

    def list_active(self) -> list[Classroom]:
        return self.filter(is_active=True)
