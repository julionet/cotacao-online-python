# Como Plugar no Service

O client é instanciado diretamente no service — **nunca** passa pelo FastAPI `Depends` e **nunca** é instanciado no router.

```python
from app.integrations.{api_name}_client import {ApiName}Client


class {Entity}Service:
    async def buscar_dados_externos(self, parametro: str) -> dict:
        client = {ApiName}Client()
        return await client.{method_name}(parametro)
```

Para APIs paginadas, o service controla a iteração:

```python
async def buscar_todas_paginas(self) -> list[dict]:
    client = {ApiName}Client()
    resultados = []
    page = 1

    while True:
        response = await client.{method_name}(page=page)
        items = response.get("data", [])
        if not items:
            break
        resultados.extend(items)
        page += 1

    return resultados
```

O nome da chave de itens (`"data"` no exemplo acima) depende do formato de resposta real da API — verifique com o usuário qual é a chave correta (ex.: `"items"`, `"results"`, `"records"`) antes de gerar o código; não assuma `"data"` sem confirmação se o formato de paginação não foi descrito em `endpoints`.

## Regras

1. **Nunca instanciar o client no router** — sempre no service
2. **Nunca mapear a resposta para Pydantic** na chamada ao client — se o service precisar devolver um schema Pydantic ao router, faça o mapeamento explicitamente no próprio service, a partir do `dict | list` bruto retornado pelo client
3. Trate exceções específicas do domínio no service, se necessário — o `BaseHttpClient` já levanta `HTTPException` para erros HTTP, timeout e falhas de conexão, então normalmente não é preciso capturar erros de rede novamente no service
4. Para APIs paginadas, pare a iteração quando a página retornar uma lista de itens vazia
