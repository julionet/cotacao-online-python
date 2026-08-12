# Skill: Criar Novo Endpoint FastAPI

Você é responsável por adicionar uma nova entidade completa a um projeto FastAPI já estruturado. Siga as instruções abaixo com precisão.

## Como Invocar

O usuário deve fornecer:

```
entidade: {NomeDaEntidade}
campos: {campo}: {tipo}, {campo}: {tipo}, ...
métodos: GET, POST, PUT, DELETE  (informar apenas os desejados)
```

**Exemplo:**
```
entidade: Product
campos: name: str, price: float, description: str, is_available: bool
métodos: GET, POST, PUT, DELETE
```

## O Que Esta Skill Faz

1. Cria `app/models/{entity}.py` — modelo SQLAlchemy
2. Cria `app/schemas/{entity}.py` — schemas Pydantic (Create, Update, Response)
3. Cria `app/repositories/{entity}_repository.py` — acesso ao banco
4. Cria `app/services/{entity}_service.py` — lógica de negócio
5. Cria `app/routers/{entity}_router.py` — endpoints HTTP
6. Registra o router em `app/main.py`

## Mapeamento de Tipos Python → SQLAlchemy

| Python     | SQLAlchemy Mapped                                           |
|------------|-------------------------------------------------------------|
| `str`      | `Mapped[str] = mapped_column(String(255))`                  |
| `int`      | `Mapped[int] = mapped_column(Integer)`                      |
| `float`    | `Mapped[float] = mapped_column(Float)`                      |
| `bool`     | `Mapped[bool] = mapped_column(Boolean)`                     |
| `date`     | `Mapped[date] = mapped_column(Date)`                        |
| `datetime` | `Mapped[datetime] = mapped_column(DateTime(timezone=True))` |

## Geração dos Arquivos

### `app/models/{entity}.py`

```python
import uuid
from sqlalchemy import String, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class {Entity}(Base):
    __tablename__ = "{entities}"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # campos fornecidos pelo usuário aqui
```

### `app/schemas/{entity}.py`

Sempre gerar três schemas:

```python
import uuid
from pydantic import BaseModel
from typing import Optional

class {Entity}Create(BaseModel):
    # campos obrigatórios para criação

class {Entity}Update(BaseModel):
    # todos os campos como Optional para atualização parcial

class {Entity}Response(BaseModel):
    id: uuid.UUID
    # todos os campos
    model_config = {"from_attributes": True}
```

### `app/repositories/{entity}_repository.py`

Incluir apenas os métodos necessários para os métodos HTTP solicitados:

- `find_by_id` — necessário para GET por ID, PUT, DELETE
- `find_all` — necessário para GET lista
- `create` — necessário para POST
- `update` — necessário para PUT
- `delete` — necessário para DELETE

```python
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.{entity} import {Entity}

class {Entity}Repository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, id: uuid.UUID) -> {Entity} | None:
        result = await self.db.execute(select({Entity}).where({Entity}.id == id))
        return result.scalar_one_or_none()

    async def find_all(self) -> list[{Entity}]:
        result = await self.db.execute(select({Entity}))
        return list(result.scalars().all())

    async def create(self, entity: {Entity}) -> {Entity}:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: {Entity}) -> {Entity}:
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity: {Entity}) -> None:
        await self.db.delete(entity)
        await self.db.commit()
```

### `app/services/{entity}_service.py`

Gerar apenas os métodos correspondentes aos HTTP solicitados:

- `GET lista` → `get_all`
- `GET por ID` → `get_by_id`
- `POST` → `create`
- `PUT` → `update`
- `DELETE` → `delete`

```python
import uuid
from fastapi import HTTPException, status
from app.repositories.{entity}_repository import {Entity}Repository
from app.schemas.{entity} import {Entity}Create, {Entity}Update
from app.models.{entity} import {Entity}

class {Entity}Service:
    def __init__(self, repository: {Entity}Repository):
        self.repository = repository

    async def get_all(self) -> list[{Entity}]:
        return await self.repository.find_all()

    async def get_by_id(self, id: uuid.UUID) -> {Entity}:
        entity = await self.repository.find_by_id(id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="{Entity} não encontrado")
        return entity

    async def create(self, data: {Entity}Create) -> {Entity}:
        entity = {Entity}(**data.model_dump())
        return await self.repository.create(entity)

    async def update(self, id: uuid.UUID, data: {Entity}Update) -> {Entity}:
        entity = await self.get_by_id(id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(entity, field, value)
        return await self.repository.update(entity)

    async def delete(self, id: uuid.UUID) -> None:
        entity = await self.get_by_id(id)
        await self.repository.delete(entity)
```

### `app/routers/{entity}_router.py`

Gerar apenas os endpoints para os métodos HTTP solicitados. Todas as rotas são protegidas por JWT.

```python
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.{entity}_repository import {Entity}Repository
from app.services.{entity}_service import {Entity}Service
from app.schemas.{entity} import {Entity}Create, {Entity}Update, {Entity}Response

router = APIRouter(prefix="/{entities}", tags=["{Entities}"])

# GET /entities
@router.get("/", response_model=list[{Entity}Response])
async def list_{entities}(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    service = {Entity}Service({Entity}Repository(db))
    return await service.get_all()

# GET /entities/{id}
@router.get("/{id}", response_model={Entity}Response)
async def get_{entity}(id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    service = {Entity}Service({Entity}Repository(db))
    return await service.get_by_id(id)

# POST /entities
@router.post("/", response_model={Entity}Response, status_code=status.HTTP_201_CREATED)
async def create_{entity}(data: {Entity}Create, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    service = {Entity}Service({Entity}Repository(db))
    return await service.create(data)

# PUT /entities/{id}
@router.put("/{id}", response_model={Entity}Response)
async def update_{entity}(id: uuid.UUID, data: {Entity}Update, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    service = {Entity}Service({Entity}Repository(db))
    return await service.update(id, data)

# DELETE /entities/{id}
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{entity}(id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    service = {Entity}Service({Entity}Repository(db))
    await service.delete(id)
```

### Registro em `app/main.py`

Após criar os arquivos, adicionar ao `main.py`:

```python
from app.routers import {entity}_router
app.include_router({entity}_router.router)
```

## Regras de Execução

1. Antes de criar qualquer arquivo, verifique se `app/main.py` existe — se não existir, informe o usuário que o projeto precisa ser scaffoldado primeiro com a skill `fastapi-scaffold`
2. Sempre adicione `id: uuid.UUID` como primeira coluna do modelo, mesmo que não informado
3. Gere **apenas** os métodos do repository, service e router que correspondem aos métodos HTTP solicitados
4. Nunca omita os `__init__.py` — verifique se existem antes de criar os arquivos
5. Sempre use `model_dump(exclude_unset=True)` no update para suportar atualização parcial
6. Sempre informe ao usuário a lista de arquivos criados e os endpoints disponíveis ao final
