# Registro no Projeto

## `app/main.py`

Após criar os arquivos, adicionar ao `main.py`. O prefixo `/api/v1` é aplicado aqui, no `include_router` — nunca dentro do `APIRouter` do próprio router de entidade:

```python
from app.routers import {entity}_router
app.include_router({entity}_router.router, prefix="/api/v1")
```

## `app/core/database.py`

Adicionar o import do novo model **antes** da função `init_db`, junto aos outros imports de models:

```python
from app.models.{entity} import {Entity}  # noqa: E402, F401
```

Isso é obrigatório para que o `Base.metadata.create_all` reconheça a nova tabela na inicialização.
