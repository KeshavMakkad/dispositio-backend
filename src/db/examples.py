"""
Example usage patterns for database session management.

This file demonstrates various ways to use the database session utilities.
"""

from typing import List

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from db import get_db, get_db_context, DatabaseSession, BaseRepository

# from db.models import YourModel  # Import your models


router = APIRouter()


# ============================================================================
# PATTERN 1: FastAPI Dependency Injection (Recommended for API endpoints)
# ============================================================================


@router.get("/items")
def get_items_endpoint(db: Session = Depends(get_db)):
    """
    Use Depends(get_db) to automatically inject a database session.
    FastAPI handles opening and closing the session.
    """
    # Use db session here
    # items = db.query(YourModel).all()
    # return items
    pass


@router.post("/items")
def create_item_endpoint(item_data: dict, db: Session = Depends(get_db)):
    """Create item with automatic session management."""
    try:
        # new_item = YourModel(**item_data)
        # db.add(new_item)
        # db.commit()
        # db.refresh(new_item)
        # return new_item
        pass
    except Exception as e:
        db.rollback()
        raise


# ============================================================================
# PATTERN 2: Context Manager (Recommended for services/background tasks)
# ============================================================================


def process_items_with_context():
    """
    Use context manager for automatic commit/rollback.
    Great for service functions and background tasks.
    """
    with get_db_context() as db:
        # Automatic commit on success, rollback on error
        # items = db.query(YourModel).filter_by(active=True).all()
        # for item in items:
        #     item.processed = True
        # Session automatically committed when exiting context
        pass


# ============================================================================
# PATTERN 3: DatabaseSession Class (Alternative context manager)
# ============================================================================


def process_items_with_class():
    """Use DatabaseSession class for session management."""
    db_manager = DatabaseSession()

    with db_manager.session() as db:
        # Automatic commit/rollback
        # items = db.query(YourModel).all()
        # return items
        pass


# ============================================================================
# PATTERN 4: BaseRepository Pattern (Recommended for complex CRUD)
# ============================================================================

# Example: Create a repository for your model
# class ItemRepository(BaseRepository[YourModel]):
#     """Custom repository with additional methods."""
#
#     def get_active_items(self) -> List[YourModel]:
#         """Get all active items."""
#         return self.filter(active=True)
#
#     def get_by_name(self, name: str) -> YourModel:
#         """Get item by name."""
#         results = self.filter(name=name)
#         return results[0] if results else None


def use_repository_in_service():
    """Use repository pattern in a service function."""
    with get_db_context() as db:
        # item_repo = ItemRepository(YourModel, db)
        #
        # # Use repository methods
        # item = item_repo.get(item_id=1)
        # all_items = item_repo.get_all(skip=0, limit=10)
        # active_items = item_repo.get_active_items()
        #
        # # Create new item
        # new_item = YourModel(name="Test", active=True)
        # created_item = item_repo.create(new_item)
        #
        # # Update item
        # updated_item = item_repo.update(1, name="Updated Name")
        #
        # # Delete item
        # item_repo.delete(1)
        pass


@router.get("/items/{item_id}")
def get_item_with_repository(item_id: int, db: Session = Depends(get_db)):
    """Combine FastAPI dependency with repository pattern."""
    # item_repo = ItemRepository(YourModel, db)
    # item = item_repo.get(item_id)
    # if not item:
    #     raise HTTPException(status_code=404, detail="Item not found")
    # return item
    pass


# ============================================================================
# PATTERN 5: Manual Session Management (Use with caution)
# ============================================================================


def manual_session_handling():
    """
    Manual session handling - only use when you need fine control.
    Remember to close the session!
    """
    db_manager = DatabaseSession()
    db = db_manager.get_session()

    try:
        # Use db session
        # items = db.query(YourModel).all()
        db.commit()
        # return items
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()  # Important!


# ============================================================================
# PATTERN 6: Nested Transactions
# ============================================================================


def nested_transaction_example():
    """Example of nested transaction handling."""
    with get_db_context() as db:
        # Outer operation
        # item1 = YourModel(name="Item 1")
        # db.add(item1)
        # db.flush()  # Flush but don't commit yet

        try:
            # Inner operation that might fail
            # item2 = YourModel(name="Item 2")
            # db.add(item2)
            # db.flush()
            #
            # # Some operation that might raise
            # risky_operation()
            pass
        except Exception as e:
            # Handle error but continue with outer transaction
            print(f"Inner operation failed: {e}")
            # Outer transaction will still commit item1


__all__ = [
    "router",
]
