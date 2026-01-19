"""
Database Initialization
"""
from sqlalchemy.orm import Session
from app.db.base_class import Base
from app.db.session import engine


def init_db() -> None:
    """
    Create all database tables
    """
    # Import all models here to ensure they are registered with Base
    from app.models import investment_tracker  # noqa

    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all database tables (use with caution!)
    """
    Base.metadata.drop_all(bind=engine)
