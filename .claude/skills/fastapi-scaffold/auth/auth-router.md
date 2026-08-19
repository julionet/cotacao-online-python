# Router de Autenticação (`app/routers/auth_router.py`)

- O prefixo `/api/v1` **não** é declarado aqui — é aplicado em `main.py` no `include_router` (ver `core/infra-files.md`). O `APIRouter` mantém apenas `prefix="/auth"`.
- `refresh` lê o refresh token do header `refresh-token` (`Header(..., alias="refresh-token")`), nunca do body.
- `forgot-password` e `reset-password` seguem o mesmo padrão de rate limiting dos demais endpoints de escrita (`request: Request` como primeiro parâmetro + `@limiter.limit(...)`).
- `reset-password` é `PUT`, não retorna `response_model` (sem corpo, status 200).

```python
from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.register(data)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.login(data)

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(refresh_token: str = Header(..., alias="refresh-token")):
    return await AuthService.refresh(refresh_token)

@router.get("/me", response_model=UserResponse)
async def me(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = AuthService(UserRepository(db))
    return await service.get_me(current_user["sub"])

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit("3/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.forgot_password(data)

@router.put("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    await service.reset_password(data)
```
