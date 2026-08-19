# Serviço de Autenticação (`app/services/auth_service.py`)

- `refresh` recebe o `refresh_token` já extraído do header pelo router (ver `auth-router.md`) — nunca um schema de body.
- `forgot_password`: se o e-mail não existir, levanta `404`. Se existir, gera o token com `generate_reset_token()`, grava `reset_token` + `reset_token_expires` (`now + settings.RESET_TOKEN_EXPIRE_MINUTES`), envia por e-mail com `send_email()` e retorna o token na resposta (`ForgotPasswordResponse`).
- `reset_password`: valida e-mail (404 se não existir), valida o `token` contra o `reset_token` armazenado e a expiração (`400` se inválido/expirado), grava o hash da nova senha e limpa `reset_token`/`reset_token_expires`. Não retorna corpo.

```python
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
)
from app.models.user import User
from app.core.config import settings
from app.core.email import send_email
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_reset_token,
)

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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário inativo")
        payload = {"sub": str(user.id), "email": user.email}
        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
        )

    @staticmethod
    async def refresh(refresh_token: str) -> AccessTokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
        new_payload = {"sub": payload["sub"], "email": payload["email"]}
        return AccessTokenResponse(access_token=create_access_token(new_payload))

    async def get_me(self, user_id: str) -> User:
        user = await self.repository.find_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        return user

    async def forgot_password(self, data: ForgotPasswordRequest) -> ForgotPasswordResponse:
        user = await self.repository.find_by_email(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        token = generate_reset_token()
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
        await self.repository.update(user)
        await send_email(
            to=user.email,
            subject="Recuperação de senha",
            body=f"Seu código de recuperação de senha é: {token}. Ele expira em {settings.RESET_TOKEN_EXPIRE_MINUTES} minutos.",
        )
        return ForgotPasswordResponse(token=token)

    async def reset_password(self, data: ResetPasswordRequest) -> None:
        user = await self.repository.find_by_email(data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        if not user.reset_token or user.reset_token != data.token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")
        if not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expirado")
        user.password = hash_password(data.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        await self.repository.update(user)
```
