from typing import Self
from datetime import datetime
from pydantic import BaseModel, Field


class BaseDBModel(BaseModel):
    """Base model with common fields."""

    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def create(cls, **data) -> Self:
        """Create new instance with validation."""
        return cls(**data)
