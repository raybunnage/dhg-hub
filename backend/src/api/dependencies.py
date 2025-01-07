from fastapi import Depends
from ..services.user import UserService


def get_user_service() -> UserService:
    return UserService()
