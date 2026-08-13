from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.login(data)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(data: RefreshRequest, current_user: dict = Depends(get_current_user)):
    service = AuthService(UserRepository(None))
    return await service.refresh(data)


@router.get("/me", response_model=UserResponse)
async def me(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = AuthService(UserRepository(db))
    return await service.get_me(current_user["sub"])
