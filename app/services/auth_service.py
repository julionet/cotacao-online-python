import uuid

from fastapi import HTTPException, status
from jose import JWTError

from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import AccessTokenResponse, LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register(self, data: UserCreate) -> User:
        existing = await self.repository.find_by_email(data.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado")
        user = User(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
        )
        return await self.repository.create(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repository.find_by_email(data.email)
        if not user or not verify_password(data.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
        payload = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
        )

    async def refresh(self, data: RefreshRequest) -> AccessTokenResponse:
        try:
            payload = decode_token(data.refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")
        new_payload = {"sub": payload["sub"], "email": payload["email"]}
        return AccessTokenResponse(access_token=create_access_token(new_payload))

    async def get_me(self, user_id: str) -> User:
        user = await self.repository.find_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recurso não encontrado")
        return user
