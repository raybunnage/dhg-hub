from typing import Optional
from .base import BaseDBModel


class User(BaseDBModel):
    """User model."""

    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
