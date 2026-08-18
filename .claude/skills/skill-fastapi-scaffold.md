# Skill: Estruturar Projeto FastAPI do Zero

Você é responsável por criar a estrutura inicial completa de um projeto FastAPI. Siga as instruções abaixo com precisão.

## Como Invocar

O usuário deve fornecer:

**Opção A – Scaffold com entidade:**
```
projeto: {nome_do_projeto}
entidade: {NomeDaEntidade}
campos: {campo}: {tipo}, {campo}: {tipo}, ...
```

**Opção B – Scaffold vazio:**
```
projeto: {nome_do_projeto}
scaffold: vazio
```

## O Que Esta Skill Faz

### Para Opção A (com entidade):

1. Cria toda a estrutura de diretórios
2. Gera todos os arquivos base (`main.py`, `config.py`, `database.py`, `security.py`, `dependencies.py`, `limiter.py`, `logging.py`, `middleware.py`)
3. Gera `requirements.txt`, `.env.example` e `.gitignore`
4. Gera o modelo `User` completo com autenticação JWT
5. Gera o router `/auth` completo (`register`, `login`, `refresh`, `me`) com rate limiting
6. Gera model, schema, repository, service e router para a entidade fornecida
7. Configura inicialização automática do banco e tabelas no startup da aplicação

### Para Opção B (vazio):

1. Cria toda a estrutura de diretórios
2. Gera todos os arquivos base
3. Gera `requirements.txt`, `.env.example` e `.gitignore`
4. Gera o modelo `User` completo com autenticação JWT
5. Gera o router `/auth` completo com rate limiting
6. **Não cria** nenhuma entidade adicional – projeto pronto para receber novas entidades
7. Configura inicialização automática do banco e tabelas no startup da aplicação

## Estrutura de Diretórios a Criar

```
{project_name}/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   ├── limiter.py
│   │   ├── logging.py
│   │   └── middleware.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── pagination.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   └── user_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── routers/
│       ├── __init__.py
│       └── auth_router.py
├── .env.example
├── .gitignore
└── requirements.txt
```

Para Opção A, adicionar dentro de `models/`, `schemas/`, `repositories/`, `services/` e `routers/` os arquivos da entidade fornecida.

## Conteúdo dos Arquivos Base

### `app/main.py`

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

app.include_router(auth_router.router)
# registrar outros routers aqui
```

### `app/core/config.py`

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

    model_config = {"env_file": ".env"}

settings = Settings()
```

### `app/core/database.py`

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

### `app/core/security.py`

```python
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
```

### `app/core/dependencies.py`

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

### `app/core/limiter.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### `app/core/logging.py`

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

### `app/core/middleware.py`

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

### `app/models/base.py`

```python
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class TimestampedModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
```

### `app/models/user.py`

```python
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TimestampedModel

class User(TimestampedModel):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
```

### `app/schemas/pagination.py`

```python
import math
from typing import Generic, TypeVar
from pydantic import BaseModel, field_validator

T = TypeVar("T")

class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20

    @field_validator("page")
    @classmethod
    def page_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Página deve ser maior que 0")
        return v

    @field_validator("size")
    @classmethod
    def size_must_be_valid(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("Tamanho deve ser entre 1 e 100")
        return v

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def build(cls, items, total: int, page: int, size: int) -> "PaginatedResponse":
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total > 0 else 0,
        )
```

### `app/schemas/auth.py`

```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

### `app/schemas/user.py`

```python
import re
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve ter pelo menos uma letra maiúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("Senha deve ter pelo menos uma letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("Senha deve ter pelo menos um número")
        if not re.search(r"[^a-zA-Z0-9]", v):
            raise ValueError("Senha deve ter pelo menos um caractere não alfanumérico")
        return v

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

### `app/repositories/base_repository.py`

```python
import uuid
from typing import Generic, Type, TypeVar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import TimestampedModel

T = TypeVar("T", bound=TimestampedModel)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def find_by_id(self, id: uuid.UUID) -> T | None:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def find_all(self, page: int = 1, size: int = 20) -> tuple[list[T], int]:
        offset = (page - 1) * size
        total = (await self.db.execute(
            select(func.count()).select_from(self.model)
        )).scalar_one()
        items = list((await self.db.execute(
            select(self.model).offset(offset).limit(size)
        )).scalars().all())
        return items, total

    async def create(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self.db.delete(entity)
        await self.db.commit()
```

### `app/repositories/user_repository.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def find_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

### `app/services/auth_service.py`

```python
import uuid
from fastapi import HTTPException, status
from jose import JWTError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

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
    async def refresh(data: RefreshRequest) -> AccessTokenResponse:
        try:
            payload = decode_token(data.refresh_token)
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
```

### `app/routers/auth_router.py`

```python
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse

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
async def refresh(data: RefreshRequest):
    return await AuthService.refresh(data)

@router.get("/me", response_model=UserResponse)
async def me(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = AuthService(UserRepository(db))
    return await service.get_me(current_user["sub"])
```

### `.env.example`

```
APP_NAME=Minha API
DEBUG=False
CORS_ORIGINS=["*"]
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### `.gitignore`

```
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

### `requirements.txt`

```
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
pydantic-settings>=2.0.0
pydantic[email]>=2.0.0
python-multipart>=0.0.9
slowapi>=0.1.9
httpx>=0.27.0
```

## Regras de Execução

1. Crie **todos** os arquivos listados, incluindo os `__init__.py` vazios
2. Para Opção B, pare após criar os arquivos base – não crie entidade extra
3. Para Opção A, após criar os arquivos base, gere os 5 arquivos da entidade (model, schema, repository, service, router) e registre o router em `main.py`
4. Ao gerar uma entidade, sempre herde de `TimestampedModel` em vez de `Base` — os campos `id`, `created_at` e `updated_at` são herdados automaticamente. Nunca repita esses campos no model da entidade
5. **Sempre importe todos os models concretos em `database.py`** antes de `init_db` ser chamado. `TimestampedModel` é abstrato e não precisa ser importado. Adicione os imports no topo do arquivo conforme os models existirem no projeto
6. O `lifespan` em `main.py` é o único lugar onde `init_db` é chamado — nunca chame em outro lugar
7. **Nunca crie o arquivo `.env`** – crie apenas `.env.example`. Se o projeto já existir e tiver um `.env`, não o sobrescreva
8. **Nunca sobrescreva um projeto existente** sem confirmar com o usuário. Se o diretório `{project_name}/` já existir, pergunte antes de prosseguir
9. Para endpoints de listagem, use `PaginationParams` como query parameter e retorne `PaginatedResponse[EntityResponse]`. Chame `BaseRepository.find_all(page, size)` no repositório e monte a resposta com `PaginatedResponse.build(...)`
10. Para novos routers de entidade, aplique `@limiter.limit("X/minute")` nos endpoints de escrita (`POST`, `PUT`, `PATCH`, `DELETE`) e inclua `request: Request` como primeiro parâmetro da função quando o decorator de limite estiver presente
11. O campo `password` nunca deve aparecer em nenhum schema de resposta
13. Sempre informe ao usuário quais arquivos foram criados ao final
