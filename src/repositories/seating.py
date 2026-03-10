from uuid import UUID

from sqlalchemy.orm import Session

from db.base import BaseRepository
from db.models import Seating


class SeatingRepository(BaseRepository[Seating]):
    def __init__(self, db: Session):
        super().__init__(Seating, db)

    def get_by_id(self, seating_id: UUID) -> Seating | None:
        return self.get(seating_id)

    def get_all_active(self) -> list[Seating]:
        return self.filter(is_active=True)
