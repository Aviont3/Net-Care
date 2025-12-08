# FILE: backend/app/models/base.py
# Base Model with Common Fields
# ============================================

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class BaseModel(Base):
    """
    Base model with common fields for all tables:
    - id (UUID primary key)
    - created_at (timestamp)
    - updated_at (timestamp)
    """

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
