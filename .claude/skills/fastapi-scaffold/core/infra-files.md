# Arquivos de Infraestrutura (`app/core/`)

## `app/main.py`

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import init_db
from app.core.limiter import limiter
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIdMiddleware
from app.routers import auth_router
# importar outros routers aqui

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Erro não tratado: %s %s", request.method, request.url, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

app.include_router(auth_router.router, prefix="/api/v1")
# registrar outros routers aqui, sempre com prefix="/api/v1"
```

`/health` nunca é versionado — é o único endpoint que fica fora do `/api/v1`.

## `app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "API"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["*"]
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    model_config = {"env_file": ".env"}

settings = Settings()
```

## `app/core/database.py`

```python
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Importar todos os models concretos aqui para que create_all os reconheça.
# TimestampedModel é abstrato — não precisa ser importado diretamente.
from app.models.user import User  # noqa: E402, F401
# from app.models.{entity} import {Entity}  – adicionar conforme novos models forem criados

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

## `app/core/security.py`

```python
import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["type"] = "access"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload["type"] = "refresh"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def generate_reset_token() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"
```

`generate_reset_token()` usa `secrets` (não `random`) por gerar um valor usado como credencial de recuperação de senha.

## `app/core/validators.py`

Validador de força de senha compartilhado entre `UserCreate` (cadastro) e `ResetPasswordRequest` (troca de senha) — nunca duplique esta regex em outro lugar.

```python
import re

def validate_password_strength(password: str) -> str:
    if len(password) < 6:
        raise ValueError("Senha deve ter pelo menos 6 caracteres")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Senha deve ter pelo menos uma letra maiúscula")
    if not re.search(r"[a-z]", password):
        raise ValueError("Senha deve ter pelo menos uma letra minúscula")
    if not re.search(r"\d", password):
        raise ValueError("Senha deve ter pelo menos um número")
    if not re.search(r"[^a-zA-Z0-9]", password):
        raise ValueError("Senha deve ter pelo menos um caractere não alfanumérico")
    return password
```

## `app/core/email.py`

Envio real de e-mail via SMTP (`aiosmtplib`), usado pelo fluxo de `forgot-password`.

```python
import logging
from email.message import EmailMessage
import aiosmtplib
from app.core.config import settings

logger = logging.getLogger(__name__)

async def send_email(to: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
    logger.info("E-mail enviado para %s", to)
```

## `app/core/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.security import decode_token

bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")
```

## `app/core/limiter.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

## `app/core/logging.py`

```python
import logging
import sys

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
```

## `app/core/middleware.py`

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = correlation_id
        return response
```
