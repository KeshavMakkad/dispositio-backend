"""Database utility functions."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm.session import Session

from db.session import get_session
from db.authorized_session import get_authorized_session


@contextmanager
def get_db_session(read_only: bool = False) -> Generator[Session, None, None]:
    """
    Get a database session with automatic commit/rollback.
    
    This function routes to the appropriate session type:
    - read_only=True: Returns a read-only session
    - read_only=False: Returns an authorized session with write permissions
    
    Args:
        read_only: If True, returns a read-only session. If False, returns authorized session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        # For reading data
        with get_db_session(read_only=True) as session:
            users = session.query(User).all()
        
        # For writing data
        with get_db_session(read_only=False) as session:
            new_user = User(name="John")
            session.add(new_user)
    """
    if read_only:
        session = get_session(read_only=True)
    else:
        session = get_authorized_session(read_only=False)
    
    try:
        yield session
        if read_only:
            session.rollback()
        else:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
