from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # Add any other fields your user model needs

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            id=data.get("id"),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )
