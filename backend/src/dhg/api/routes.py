from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..services.user import UserService
from ..schemas.user import UserCreate, UserResponse
from .dependencies import get_user_service

router = APIRouter()


@router.get("/users", response_model=List[UserResponse])
async def get_users(service: UserService = Depends(get_user_service)):
    """Get all users."""
    return await service.get_all()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
    service = UserService()
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate, service: UserService = Depends(get_user_service)
):
    """Create a new user."""
    return await service.create(user.model_dump())


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
