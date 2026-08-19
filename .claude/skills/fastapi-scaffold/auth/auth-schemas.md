# Schemas de Autenticação (`app/schemas/`)

## `app/schemas/pagination.py`

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

## `app/schemas/user.py`

A validação de força de senha vive em `app/core/validators.py::validate_password_strength` — importe e reutilize, nunca reescreva a regex aqui.

```python
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from app.core.validators import validate_password_strength

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

## `app/schemas/auth.py`

`RefreshRequest` **não existe mais** — o refresh token passou a ser lido do header `refresh-token` (ver `auth/auth-router.md`), nunca do body.

```python
from pydantic import BaseModel, EmailStr, field_validator
from app.core.validators import validate_password_strength

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)
```
