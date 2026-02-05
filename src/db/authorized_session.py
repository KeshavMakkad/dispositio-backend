"""Authorized database session management."""

from sqlalchemy import text
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session, sessionmaker

from core.db_core import engine
from contextvars import ContextVar

# Context variable for scoping sessions
context: ContextVar[str] = ContextVar("authorized_session_context", default="default")

SQLALCHEMY_SESSION_OPTIONS = {
    "autocommit": False,
    "autoflush": False,
    "expire_on_commit": False,
}


def get_authorized_session() -> Session:
    """
    Get an authorized database session for write operations.
    
    Args:
        read_only: If True, returns a read-only session
    
    Returns:
        Session: SQLAlchemy database session with write permissions
    """
    # For now, using the same engine
    # You can add authorization logic here later
    session_engine = engine
    
    session = scoped_session(
        sessionmaker(bind=session_engine, **SQLALCHEMY_SESSION_OPTIONS),
        scopefunc=lambda: context.get(),
    )()

    return session
