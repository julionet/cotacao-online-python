# Repositórios (`app/repositories/`)

## `app/repositories/base_repository.py`

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

## `app/repositories/user_repository.py`

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

`forgot_password` e `reset_password` (em `auth-service.md`) reutilizam `update()` da `BaseRepository` para persistir `reset_token`/`reset_token_expires` e a nova senha — não crie métodos extras no repository para isso.
