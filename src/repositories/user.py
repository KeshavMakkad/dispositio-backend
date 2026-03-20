from uuid import UUID

from sqlalchemy.orm import Session

from db.base import BaseRepository
from db.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        users = self.filter(email=email)
        return users[0] if users else None

    def list_users(self) -> list[User]:
        return self.get_all(skip=0, limit=1000)

    def deactivate_user(self, user_id: UUID, updated_by: UUID) -> User | None:
        return self.update(user_id, is_active=False, updated_by=updated_by)
