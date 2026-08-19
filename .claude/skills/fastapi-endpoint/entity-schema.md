# Schema da Entidade (`app/schemas/{entity}.py`)

Sempre gerar três schemas. O `Response` sempre inclui `id`, `created_at` e `updated_at`. Campos opcionais usam a sintaxe `{tipo} | None = None` (mesmo padrão já usado em `User.reset_token` no scaffold) — não importe `Optional` de `typing`.

```python
import uuid
from datetime import datetime
from pydantic import BaseModel

class {Entity}Create(BaseModel):
    ...  # campos obrigatórios para criação

class {Entity}Update(BaseModel):
    ...  # todos os campos como {tipo} | None = None, para atualização parcial

class {Entity}Response(BaseModel):
    id: uuid.UUID
    ...  # todos os campos
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
```

O campo `password` nunca deve aparecer em `{Entity}Response` nem em nenhum outro schema de resposta.
