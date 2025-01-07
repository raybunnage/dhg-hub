from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..services.user import UserService
from ..models.user import User

router = APIRouter()


@router.get("/users", response_model=List[User])
async def get_users():
    """Get all users."""
    service = UserService()
    return await service.get_all()


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID."""
    service = UserService()
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=User)
async def create_user(user: User):
    """Create a new user."""
    service = UserService()
    return await service.create(user.model_dump())
