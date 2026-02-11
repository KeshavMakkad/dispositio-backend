"""Database session management utilities."""


from sqlalchemy import text
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import Session, sessionmaker

from core.db_core import engine
from contextvars import ContextVar

# Context variable for scoping sessions
context: ContextVar[str] = ContextVar("session_context", default="default")

SQLALCHEMY_SESSION_OPTIONS = {
    "autocommit": False,
    "autoflush": False,
    "expire_on_commit": False,
}


def get_session() -> Session:
    """
    Get a read-only database session.
    
    Returns:
        Session: SQLAlchemy database session with read-only access
    """
    session_engine = engine
    
    session = scoped_session(
        sessionmaker(bind=session_engine, **SQLALCHEMY_SESSION_OPTIONS),
        scopefunc=lambda: context.get(),
    )()
    
    session.execute(text("SET TRANSACTION READ ONLY"))
    
    return session
