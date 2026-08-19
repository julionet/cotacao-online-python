# Service da Entidade (`app/services/{entity}_service.py`)

Gerar apenas os métodos correspondentes aos HTTP solicitados:

- `GET lista` → `get_all(page, size)` — sempre com paginação, retorna `tuple[list, int]`
- `GET por ID` → `get_by_id`
- `POST` → `create`
- `PUT` → `update`
- `DELETE` → `delete`

## Validação de unicidade

Para cada campo marcado como `unique` na invocação, `create` e `update` validam duplicidade contra a base **antes** de gravar, usando o `find_by_{field}` correspondente (`entity-repository.md`). Em caso de conflito, levanta `HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um registro com esse {field}")`.

No `update`, a checagem só roda se o campo estiver presente no payload (`exclude_unset=True`) **e** o valor for diferente do atual — evita falso positivo quando o cliente reenvia o mesmo valor que a entidade já tem.

Se a entidade não tiver nenhum campo `unique`, omita completamente os blocos marcados abaixo — `create` e `update` ficam exatamente como no template sem validação.

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
        # --- bloco por campo unique (repita para cada um) ---
        existing = await self.repository.find_by_{field}(data.{field})
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um registro com esse {field}")
        # --- fim do bloco ---
        entity = {Entity}(**data.model_dump())
        return await self.repository.create(entity)

    async def update(self, id: uuid.UUID, data: {Entity}Update) -> {Entity}:
        entity = await self.get_by_id(id)
        update_data = data.model_dump(exclude_unset=True)
        # --- bloco por campo unique (repita para cada um) ---
        if "{field}" in update_data and update_data["{field}"] != getattr(entity, "{field}"):
            existing = await self.repository.find_by_{field}(update_data["{field}"])
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe um registro com esse {field}")
        # --- fim do bloco ---
        for field, value in update_data.items():
            setattr(entity, field, value)
        return await self.repository.update(entity)

    async def delete(self, id: uuid.UUID) -> None:
        entity = await self.get_by_id(id)
        await self.repository.delete(entity)
```
