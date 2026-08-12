# Skill: Integração com API Externa via httpx

Você é responsável por criar a integração com uma API externa em um projeto Python. Siga as instruções abaixo com precisão.

## Como Invocar

O usuário deve fornecer:

```
api: {NomeDaApi}
base_url: {URL base da API}
autenticação: api_key | bearer_token | nenhuma
header_name: {nome do header}  (apenas para api_key)
endpoints: {descrição dos endpoints a consumir}
timeout: {segundos}  (opcional, padrão 20)
paginada: sim | não
```

**Exemplo:**
```
api: ViaCep
base_url: https://viacep.com.br/ws
autenticação: nenhuma
endpoints: GET /{cep}/json — busca endereço por CEP
paginada: não
```

## O Que Esta Skill Faz

1. Verifica se `app/integrations/` existe — cria se não existir
2. Verifica se `app/integrations/base_client.py` existe — cria se não existir
3. Cria `app/integrations/{api_name}_client.py`
4. Adiciona variáveis ao `.env` e `.env.example`
5. Adiciona campos em `app/core/config.py`
6. Orienta como instanciar o client no service correspondente

## Estrutura da Camada `integrations/`

```
app/
└── integrations/
    ├── __init__.py
    ├── base_client.py
    └── {api_name}_client.py
```

## Conteúdo dos Arquivos

### `app/integrations/base_client.py`

```python
import asyncio
import httpx
from fastapi import HTTPException, status


class BaseHttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 20.0,
        auth_type: str | None = None,
        api_key: str | None = None,
        api_key_header: str | None = None,
        bearer_token: str | None = None,
        max_retries: int = 3,
        retry_wait: float = 2.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth_type = auth_type
        self.api_key = api_key
        self.api_key_header = api_key_header
        self.bearer_token = bearer_token
        self.max_retries = max_retries
        self.retry_wait = retry_wait

    def _build_headers(self) -> dict:
        headers = {}
        if self.auth_type == "api_key" and self.api_key and self.api_key_header:
            headers[self.api_key_header] = self.api_key
        elif self.auth_type == "bearer_token" and self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
    ) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = self._build_headers()
        attempt = 0

        while attempt < self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json,
                    )

                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erro na API externa: {response.text}",
                    )

                return response.json()

            except httpx.TimeoutException:
                attempt += 1
                if attempt >= self.max_retries:
                    raise HTTPException(
                        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                        detail=f"API externa não respondeu após {self.max_retries} tentativas",
                    )
                await asyncio.sleep(self.retry_wait)

    async def get(self, path: str, params: dict | None = None) -> dict:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict | None = None) -> dict:
        return await self._request("POST", path, json=json)

    async def put(self, path: str, json: dict | None = None) -> dict:
        return await self._request("PUT", path, json=json)

    async def delete(self, path: str) -> dict:
        return await self._request("DELETE", path)
```

### `app/integrations/{api_name}_client.py`

Padrão para API **sem paginação**:

```python
from app.integrations.base_client import BaseHttpClient
from app.core.config import settings


class {ApiName}Client(BaseHttpClient):
    def __init__(self):
        super().__init__(
            base_url=settings.{API_NAME}_BASE_URL,
            timeout=settings.{API_NAME}_TIMEOUT,
            auth_type="{api_key | bearer_token | None}",
            api_key=settings.{API_NAME}_API_KEY,            # apenas para api_key
            api_key_header=settings.{API_NAME}_KEY_HEADER,  # apenas para api_key
            bearer_token=settings.{API_NAME}_TOKEN,         # apenas para bearer_token
        )

    async def {method_name}(self, {params}) -> dict:
        return await self.get("/{path}")
```

Padrão para API **com paginação**:

```python
from app.integrations.base_client import BaseHttpClient
from app.core.config import settings


class {ApiName}Client(BaseHttpClient):
    def __init__(self):
        super().__init__(
            base_url=settings.{API_NAME}_BASE_URL,
            timeout=settings.{API_NAME}_TIMEOUT,
            auth_type="{api_key | bearer_token | None}",
        )

    async def {method_name}(self, page: int = 1, limit: int = 20, **filters) -> dict:
        params = {"page": page, "limit": limit, **filters}
        return await self.get("/{path}", params=params)
```

O service é responsável por iterar as páginas. O cliente expõe apenas uma página por chamada.

## Variáveis de Ambiente

Adicionar ao `.env` e `.env.example` da aplicação:

**API Key:**
```
{API_NAME}_BASE_URL=https://api.exemplo.com
{API_NAME}_API_KEY=sua-api-key
{API_NAME}_KEY_HEADER=X-API-Key
{API_NAME}_TIMEOUT=20
```

**Bearer Token:**
```
{API_NAME}_BASE_URL=https://api.exemplo.com
{API_NAME}_TOKEN=seu-bearer-token
{API_NAME}_TIMEOUT=20
```

Adicionar os campos correspondentes em `app/core/config.py`:

```python
{API_NAME}_BASE_URL: str
{API_NAME}_API_KEY: str | None = None
{API_NAME}_KEY_HEADER: str | None = None
{API_NAME}_TOKEN: str | None = None
{API_NAME}_TIMEOUT: float = 20.0
```

## Como Plugar no Service

O client é instanciado diretamente no service — não passa pelo FastAPI `Depends`.

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

## Regras de Execução

1. **Nunca instanciar o client no router** — sempre no service
2. **Nunca mapear a resposta para Pydantic** nesta camada — retornar `dict` bruto
3. **Nunca fazer retry em erros 4xx** — retry apenas em `httpx.TimeoutException`
4. **Sempre adicionar as variáveis ao `.env.example`** ao criar um novo client
5. **Sempre usar `settings`** para URL base, token e timeout — nunca hardcode
6. **Para APIs paginadas**, o client expõe uma página por chamada — o service decide quantas páginas buscar
7. **O nome do header de API Key é sempre configurável** via variável de ambiente — nunca fixo no código
8. **Sempre informar ao usuário** quais variáveis precisam ser preenchidas no `.env` ao final
