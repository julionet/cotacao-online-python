# Client da API — `app/integrations/{api_name}_client.py`

Escolha o template conforme o valor de `paginada` informado na invocação.

## Padrão para API **sem paginação**

```python
from app.integrations.base_client import BaseHttpClient
from app.core.config import settings


class {ApiName}Client(BaseHttpClient):
    def __init__(self):
        super().__init__(
            base_url=settings.{API_NAME}_BASE_URL,
            timeout=settings.{API_NAME}_TIMEOUT,
            auth_type="{api_key | bearer_token | oauth2 | None}",
            api_key=settings.{API_NAME}_API_KEY,             # apenas para api_key
            api_key_header=settings.{API_NAME}_KEY_HEADER,   # apenas para api_key
            bearer_token=settings.{API_NAME}_TOKEN,          # apenas para bearer_token
            token_url=settings.{API_NAME}_TOKEN_URL,         # apenas para oauth2
            client_id=settings.{API_NAME}_CLIENT_ID,         # apenas para oauth2
            client_secret=settings.{API_NAME}_CLIENT_SECRET, # apenas para oauth2
        )

    async def {method_name}(self, {params}) -> dict:
        return await self.get("/{path}")
```

## Padrão para API **com paginação**

```python
from app.integrations.base_client import BaseHttpClient
from app.core.config import settings


class {ApiName}Client(BaseHttpClient):
    def __init__(self):
        super().__init__(
            base_url=settings.{API_NAME}_BASE_URL,
            timeout=settings.{API_NAME}_TIMEOUT,
            auth_type="{api_key | bearer_token | oauth2 | None}",
        )

    async def {method_name}(self, page: int = 1, limit: int = 20, **filters) -> dict:
        params = {"page": page, "limit": limit, **filters}
        return await self.get("/{path}", params=params)
```

O service é responsável por iterar as páginas — veja `service-integration.md`. O client expõe apenas uma página por chamada.

## Regras Específicas do Client

1. Passe apenas os argumentos de `super().__init__(...)` relevantes ao `auth_type` escolhido — não inclua `api_key`/`bearer_token`/`token_url` etc. quando não usados
2. Gere um método assíncrono por endpoint descrito em `endpoints` na invocação — o nome do método deve refletir a ação (ex.: `buscar_por_cep`, `listar_pedidos`)
3. Use `self.get` / `self.post` / `self.post_form` / `self.put` / `self.patch` / `self.delete` conforme o verbo HTTP do endpoint — nunca chame `self._request` diretamente a partir do client concreto
4. O retorno é sempre `dict | list` bruto — nunca mapeie para um schema Pydantic nesta camada (isso é responsabilidade do service)
