"""Database session management utilities."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session, sessionmaker

from core.db_core import engine

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields a database session.
    
    Usage in FastAPI:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            # Use db session here
            pass
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db_context() as db:
            # Use db session here
            db.query(Model).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


class DatabaseSession:
    """
    Database session manager class for non-FastAPI contexts.
    
    Usage:
        db_manager = DatabaseSession()
        with db_manager.session() as db:
            # Use db session here
            results = db.query(Model).all()
    """
    
    def __init__(self):
        """Initialize the database session manager."""
        self._session_factory = SessionLocal
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic commit/rollback.
        
        Yields:
            Session: SQLAlchemy database session
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session(self) -> Session:
        """
        Get a raw database session (caller is responsible for closing).
        
        Returns:
            Session: SQLAlchemy database session
        """
        return self._session_factory()


__all__ = [
    "SessionLocal",
    "get_db",
    "get_db_context",
    "DatabaseSession",
]
