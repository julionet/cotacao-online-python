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

1. Cria `app/models/{entity}.py` — modelo SQLAlchemy herdando de `TimestampedModel`
2. Cria `app/schemas/{entity}.py` — schemas Pydantic (Create, Update, Response com timestamps)
3. Cria `app/repositories/{entity}_repository.py` — repositório herdando de `BaseRepository`
4. Cria `app/services/{entity}_service.py` — lógica de negócio com paginação
5. Cria `app/routers/{entity}_router.py` — endpoints HTTP com paginação e rate limiting
6. Registra o router em `app/main.py`
7. Adiciona import do model em `app/core/database.py`

## Mapeamento de Tipos Python → SQLAlchemy

| Python     | SQLAlchemy Mapped                                           |
|------------|-------------------------------------------------------------|
| `str`      | `Mapped[str] = mapped_column(String(255))`                  |
| `int`      | `Mapped[int] = mapped_column(Integer)`                      |
| `float`    | `Mapped[float] = mapped_column(Float)`                      |
| `bool`     | `Mapped[bool] = mapped_column(Boolean)`                     |
| `date`     | `Mapped[date] = mapped_column(Date)`                        |
| `datetime` | `Mapped[datetime] = mapped_column(DateTime(timezone=True))` |
| `Decimal`  | `Mapped[Decimal] = mapped_column(Numeric(10, 2))`           |
| `Text`     | `Mapped[str] = mapped_column(Text)`                         |

## Geração dos Arquivos

### `app/models/{entity}.py`

Sempre herdar de `TimestampedModel`. Os campos `id`, `created_at` e `updated_at` são herdados automaticamente — **nunca** repeti-los no model.

```python
from sqlalchemy import String, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import TimestampedModel

class {Entity}(TimestampedModel):
    __tablename__ = "{entities}"

    # campos fornecidos pelo usuário aqui
```

### `app/schemas/{entity}.py`

Sempre gerar três schemas. O `Response` sempre inclui `id`, `created_at` e `updated_at`.

```python
import uuid
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class {Entity}Create(BaseModel):
    # campos obrigatórios para criação

class {Entity}Update(BaseModel):
    # todos os campos como Optional para atualização parcial

class {Entity}Response(BaseModel):
    id: uuid.UUID
    # todos os campos
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
```

### `app/repositories/{entity}_repository.py`

Sempre herdar de `BaseRepository[{Entity}]`. Os métodos `find_by_id`, `find_all` (com paginação), `create`, `update` e `delete` já existem na classe pai. Adicione apenas métodos específicos da entidade.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.{entity} import {Entity}
from app.repositories.base_repository import BaseRepository

class {Entity}Repository(BaseRepository[{Entity}]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, {Entity})

    # Adicionar aqui apenas métodos específicos desta entidade,
    # como find_by_email, find_by_name, etc.
```

### `app/services/{entity}_service.py`

Gerar apenas os métodos correspondentes aos HTTP solicitados:

- `GET lista` → `get_all(page, size)` — sempre com paginação, retorna `tuple[list, int]`
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

    async def get_all(self, page: int = 1, size: int = 20) -> tuple[list[{Entity}], int]:
        return await self.repository.find_all(page, size)

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

Gerar apenas os endpoints para os métodos HTTP solicitados. Todas as rotas são protegidas por JWT. Endpoints de escrita (`POST`, `PUT`, `DELETE`) usam rate limiting — inclua `request: Request` como primeiro parâmetro nesses casos.

- Listagem usa `PaginationParams` como query parameter e retorna `PaginatedResponse[{Entity}Response]`
- Escrita aplica `@limiter.limit("30/minute")` nos endpoints `POST`, `PUT`, `DELETE`

```python
import uuid
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.limiter import limiter
from app.repositories.{entity}_repository import {Entity}Repository
from app.services.{entity}_service import {Entity}Service
from app.schemas.{entity} import {Entity}Create, {Entity}Update, {Entity}Response
from app.schemas.pagination import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/{entities}", tags=["{Entities}"])

# GET /entities — listagem paginada
@router.get("/", response_model=PaginatedResponse[{Entity}Response])
async def list_{entities}(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = {Entity}Service({Entity}Repository(db))
    items, total = await service.get_all(pagination.page, pagination.size)
    return PaginatedResponse.build(items, total, pagination.page, pagination.size)

# GET /entities/{id}
@router.get("/{id}", response_model={Entity}Response)
async def get_{entity}(id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    service = {Entity}Service({Entity}Repository(db))
    return await service.get_by_id(id)

# POST /entities
@router.post("/", response_model={Entity}Response, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_{entity}(
    request: Request,
    data: {Entity}Create,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = {Entity}Service({Entity}Repository(db))
    return await service.create(data)

# PUT /entities/{id}
@router.put("/{id}", response_model={Entity}Response)
@limiter.limit("30/minute")
async def update_{entity}(
    request: Request,
    id: uuid.UUID,
    data: {Entity}Update,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = {Entity}Service({Entity}Repository(db))
    return await service.update(id, data)

# DELETE /entities/{id}
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_{entity}(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    service = {Entity}Service({Entity}Repository(db))
    await service.delete(id)
```

### Registro em `app/main.py`

Após criar os arquivos, adicionar ao `main.py`:

```python
from app.routers import {entity}_router
app.include_router({entity}_router.router)
```

### Import em `app/core/database.py`

Adicionar o import do novo model **antes** da função `init_db`, junto aos outros imports de models:

```python
from app.models.{entity} import {Entity}  # noqa: E402, F401
```

Isso é obrigatório para que o `Base.metadata.create_all` reconheça a nova tabela na inicialização.

## Regras de Execução

1. Antes de criar qualquer arquivo, verifique se `app/main.py` existe — se não existir, informe o usuário que o projeto precisa ser scaffoldado primeiro com o agente `fastapi-scaffold`
2. Sempre herde de `TimestampedModel` — **nunca** de `Base`. Os campos `id`, `created_at` e `updated_at` são herdados automaticamente; não os declare no model
3. Sempre herde o repository de `BaseRepository[{Entity}]` — não reimplemente `find_by_id`, `find_all`, `create`, `update` e `delete` se já existem na classe pai
4. Sempre use paginação no endpoint de listagem (`GET /`) com `PaginationParams` e `PaginatedResponse`
5. Aplique `@limiter.limit("30/minute")` e inclua `request: Request` nos endpoints de escrita: `POST`, `PUT`, `DELETE`
6. O schema `Response` sempre inclui `id: uuid.UUID`, `created_at: datetime` e `updated_at: datetime`
7. Gere **apenas** os métodos do repository, service e router que correspondem aos métodos HTTP solicitados pelo usuário
8. Nunca omita os `__init__.py` — verifique se existem antes de criar os arquivos
9. Sempre use `model_dump(exclude_unset=True)` no update para suportar atualização parcial
10. Sempre adicione o import do novo model em `app/core/database.py` para garantir que a tabela seja criada no startup
11. O campo `password` nunca deve aparecer em nenhum schema de resposta
12. Sempre informe ao usuário a lista de arquivos criados/modificados e os endpoints disponíveis ao final
