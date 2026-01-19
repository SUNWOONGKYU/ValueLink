"""
SQLAlchemy Base Class
"""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: Any
    __name__: str

    # Auto-generate table name from class name
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Common timestamp columns
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
