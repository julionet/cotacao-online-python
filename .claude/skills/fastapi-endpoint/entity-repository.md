# Repository da Entidade (`app/repositories/{entity}_repository.py`)

Sempre herdar de `BaseRepository[{Entity}]`. Os métodos `find_by_id`, `find_all` (com paginação), `create`, `update` e `delete` já existem na classe pai. Adicione apenas métodos específicos da entidade.

**Para cada campo marcado como `unique`** no `campos:` da invocação, adicione um método `find_by_{field}` — ele é usado pelo service (`entity-service.md`) para validar duplicidade antes de criar/atualizar. Se a entidade não tiver nenhum campo `unique`, omita esses métodos.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.{entity} import {Entity}
from app.repositories.base_repository import BaseRepository

class {Entity}Repository(BaseRepository[{Entity}]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, {Entity})

    # Repita este método para cada campo declarado como unique
    async def find_by_{field}(self, {field}: {type}) -> {Entity} | None:
        result = await self.db.execute(
            select({Entity}).where({Entity}.{field} == {field})
        )
        return result.scalar_one_or_none()
```
