# Router da Entidade (`app/routers/{entity}_router.py`)

Gerar apenas os endpoints para os métodos HTTP solicitados. Todas as rotas são protegidas por JWT. Endpoints de escrita (`POST`, `PUT`, `DELETE`) usam rate limiting — inclua `request: Request` como primeiro parâmetro nesses casos.

- Listagem usa `PaginationParams` como query parameter e retorna `PaginatedResponse[{Entity}Response]`
- Escrita aplica `@limiter.limit("30/minute")` nos endpoints `POST`, `PUT`, `DELETE`
- Se a entidade tiver campos `unique`, `POST` e `PUT` podem retornar `409 Conflict` — isso é tratado inteiramente no service (`entity-service.md`); o router não precisa de nenhuma lógica extra para isso

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
