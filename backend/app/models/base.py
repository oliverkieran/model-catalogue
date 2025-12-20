"""
SQLModel Base Configuration and Mixins
All models inherit from SQLModel or use mixins for common functionality
"""

from sqlmodel import SQLModel, Field
from datetime import datetime
from sqlalchemy import DateTime, func


class TimestampMixin(SQLModel):
    """
    Mixin that adds created_at and updated_at timestamps to models

    Usage:
        class MyModel(BaseClass, TimestampMixin, table=True):
            id: int | None = Field(default=None, primary_key=True)
            name: str

    Note: This mixin should NOT inherit from SQLModel to avoid multiple inheritance issues.
    """

    created_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
        },
        sa_type=DateTime(timezone=True),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": func.now(),
        },
        sa_type=DateTime(timezone=True),
    )
