"""Database session management utilities."""

from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import SQLAlchemyError
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


def get_session(read_only: bool = False) -> Session:
    """
    Get a database session.
    
    Args:
        read_only: If True, returns a read-only session with automatic rollback
    
    Returns:
        Session: SQLAlchemy database session
    """
    session_engine = engine
    
    session = scoped_session(
        sessionmaker(bind=session_engine, **SQLALCHEMY_SESSION_OPTIONS),
        scopefunc=lambda: context.get(),
    )()
    
    if read_only:
        session.execute(text("SET TRANSACTION READ ONLY"))
    
    return session


def get_db_health(engine: Engine) -> bool | None:
    """
    Check database health.
    
    Args:
        engine: SQLAlchemy engine to check
        
    Returns:
        bool | None: True if healthy, False if unhealthy, None if error
    """
    try:
        with engine.connect():
            return engine.pool.overflow() < engine.pool._max_overflow
    except (SQLAlchemyError, ConnectionRefusedError):
        return None


def get_db_status(engine: Engine) -> str:
    """
    Get database pool status.
    
    Args:
        engine: SQLAlchemy engine to check
        
    Returns:
        str: Pool status string
    """
    return engine.pool.status()
