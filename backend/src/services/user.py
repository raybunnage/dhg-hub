from .base import BaseService
from ..models.user import User


class UserService(BaseService[User]):
    """User service with specific user operations."""

    def __init__(self):
        super().__init__("users")

    async def get_by_email(self, email: str) -> User:
        """Get user by email."""
        response = (
            self.client.table(self.table).select("*").eq("email", email).execute()
        )
        return User.model_validate(response.data[0]) if response.data else None
