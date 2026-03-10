from sqlalchemy.orm import Session

from db.base import BaseRepository
from db.models import Classroom


class ClassroomRepository(BaseRepository[Classroom]):
    def __init__(self, db: Session):
        super().__init__(Classroom, db)

    def get_by_name(self, name: str) -> Classroom | None:
        results = self.filter(classroom_name=name)
        return results[0] if results else None
