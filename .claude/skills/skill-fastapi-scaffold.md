# Skill: Estruturar Projeto FastAPI do Zero

Você é responsável por criar a estrutura inicial completa de um projeto FastAPI. Siga as instruções abaixo com precisão.

## Como Invocar

O usuário deve fornecer:

**Opção A — Scaffold com entidade:**
```
projeto: {nome_do_projeto}
entidade: {NomeDaEntidade}
campos: {campo}: {tipo}, {campo}: {tipo}, ...
```

**Opção B — Scaffold vazio:**
```
projeto: {nome_do_projeto}
scaffold: vazio
```

## O Que Esta Skill Faz

### Para Opção A (com entidade):

1. Cria toda a estrutura de diretórios
2. Gera todos os arquivos base (`main.py`, `config.py`, `database.py`, `security.py`, `dependencies.py`)
3. Gera `requirements.txt` e `.env.example`
4. Gera o modelo `User` completo com autenticação JWT
5. Gera o router `/auth` completo (`register`, `login`, `refresh`, `me`)
6. Gera model, schema, repository, service e router para a entidade fornecida
7. Configura inicialização automática do banco e tabelas no startup da aplicação

### Para Opção B (vazio):

1. Cria toda a estrutura de diretórios
2. Gera todos os arquivos base (`main.py`, `config.py`, `database.py`, `security.py`, `dependencies.py`)
3. Gera `requirements.txt` e `.env.example`
4. Gera o modelo `User` completo com autenticação JWT
5. Gera o router `/auth` completo
6. **Não cria** nenhuma entidade adicional — projeto pronto para receber novas entidades
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
│   │   └── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── auth_service.py
│   └── routers/
│       ├── __init__.py
│       └── auth_router.py
├── .env
├── .env.example
└── requirements.txt
```

Para Opção A, adicionar dentro de `models/`, `schemas/`, `repositories/`, `services/` e `routers/` os arquivos da entidade fornecida.

## Conteúdo dos Arquivos Base

### `app/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import init_db
from app.routers import auth_router
# importar outros routers aqui

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="{ProjectName} API", lifespan=lifespan)

app.include_router(auth_router.router)
# registrar outros routers aqui
```

### `app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# Importar todos os models aqui para que create_all os reconheça
from app.models.user import User  # noqa: E402, F401
# from app.models.{entity} import {Entity}  — adicionar conforme novos models forem criados

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
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

### `app/models/user.py`

```python
import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
import uuid
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}
```

### `app/repositories/user_repository.py`

```python
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

### `app/services/auth_service.py`

```python
import uuid
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from jose import JWTError

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

    async def refresh(self, data: RefreshRequest) -> AccessTokenResponse:
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
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.register(data)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(UserRepository(db))
    return await service.login(data)

@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(data: RefreshRequest):
    service = AuthService(UserRepository(None))
    return await service.refresh(data)

@router.get("/me", response_model=UserResponse)
async def me(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = AuthService(UserRepository(db))
    return await service.get_me(current_user["sub"])
```

### `.env.example`

```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
SECRET_KEY=sua-chave-secreta-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### `requirements.txt`

```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
python-jose[cryptography]
passlib[bcrypt]
pydantic-settings
pydantic[email]
httpx
```

## Regras de Execução

1. Crie **todos** os arquivos listados, incluindo os `__init__.py` vazios
2. Para Opção B, pare após criar os arquivos base — não crie entidade extra
3. Para Opção A, após criar os arquivos base, gere os 5 arquivos da entidade (model, schema, repository, service, router) e registre o router em `main.py`
4. Ao gerar uma entidade, sempre adicione `id: uuid.UUID` como chave primária mesmo que o usuário não tenha especificado
5. **Sempre importe todos os models em `database.py`** antes de `init_db` ser chamado — o SQLAlchemy só cria as tabelas dos models que foram importados. Adicione os imports no topo do arquivo conforme os models existirem no projeto
6. O `lifespan` em `main.py` é o único lugar onde `init_db` é chamado — nunca chame em outro lugar
7. Sempre informe ao usuário quais arquivos foram criados ao final
