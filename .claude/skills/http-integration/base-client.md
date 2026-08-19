# Base Client — `app/integrations/base_client.py`

Criado **uma única vez por projeto**, na primeira integração externa. Todas as integrações seguintes reutilizam esta classe herdando dela — nunca duplique a lógica de retry/autenticação em cada client.

Segue o mesmo padrão de logging e backoff exponencial já usado em `app/services/exchange_service.py` (`logger = logging.getLogger(__name__)`, `_BACKOFF = (1, 2, 4)`), para manter consistência com o restante do projeto.

```python
import asyncio
import logging
import time

import httpx
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

RETRY_ON_STATUS = {502, 503, 504}
_BACKOFF = (1, 2, 4)


class BaseHttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 20.0,
        auth_type: str | None = None,
        api_key: str | None = None,
        api_key_header: str | None = None,
        bearer_token: str | None = None,
        token_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth_type = auth_type
        self.api_key = api_key
        self.api_key_header = api_key_header
        self.bearer_token = bearer_token
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._oauth2_token: str | None = None
        self._token_expires_at: float = 0.0

    def _build_headers(self) -> dict:
        headers = {}
        if self.auth_type == "api_key" and self.api_key and self.api_key_header:
            headers[self.api_key_header] = self.api_key
        elif self.auth_type == "bearer_token" and self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.auth_type == "oauth2" and self._oauth2_token:
            headers["Authorization"] = f"Bearer {self._oauth2_token}"
        return headers

    async def _refresh_oauth2_token(self) -> None:
        if self._oauth2_token and time.monotonic() < self._token_expires_at:
            return

        logger.info("Refreshing OAuth2 token from %s", self.token_url)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

        if response.status_code >= 400:
            error_msg = f"Falha ao obter token OAuth2: {response.status_code} {response.text}"
            logger.error(error_msg)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_msg)

        payload = response.json()
        self._oauth2_token = payload["access_token"]
        expires_in = payload.get("expires_in", 3600)
        self._token_expires_at = time.monotonic() + expires_in - 30

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
        data: dict | None = None,
    ) -> dict | list:
        if self.auth_type == "oauth2":
            await self._refresh_oauth2_token()

        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = self._build_headers()
        last_exc: HTTPException | None = None
        response: httpx.Response | None = None

        for attempt in range(len(_BACKOFF) + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json,
                        data=data,
                    )
                    response.raise_for_status()
                break

            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                error_msg = f"Erro na API externa: {status_code} {exc.response.text}"
                if status_code not in RETRY_ON_STATUS:
                    logger.error(error_msg)
                    raise HTTPException(status_code=status_code, detail=error_msg) from exc
                logger.warning("%s (tentativa %d)", error_msg, attempt + 1)
                last_exc = HTTPException(status_code=status_code, detail=error_msg)

            except httpx.TimeoutException:
                error_msg = f"{method} {url} não respondeu (timeout)"
                logger.warning("%s (tentativa %d)", error_msg, attempt + 1)
                last_exc = HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f"API externa não respondeu após {len(_BACKOFF) + 1} tentativas",
                )

            except httpx.RequestError as exc:
                error_msg = f"Erro de conexão com {url}: {exc}"
                logger.warning("%s (tentativa %d)", error_msg, attempt + 1)
                last_exc = HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_msg)

            if attempt < len(_BACKOFF):
                await asyncio.sleep(_BACKOFF[attempt])
            else:
                logger.error("Esgotadas as tentativas para %s %s", method, url)
                raise last_exc  # type: ignore[misc]

        try:
            return response.json()  # type: ignore[union-attr]
        except ValueError as exc:
            error_msg = f"Resposta inválida (JSON malformado) de {url}"
            logger.error(error_msg)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=error_msg) from exc

    async def get(self, path: str, params: dict | None = None) -> dict | list:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, json: dict | None = None) -> dict | list:
        return await self._request("POST", path, json=json)

    async def post_form(self, path: str, data: dict) -> dict | list:
        return await self._request("POST", path, data=data)

    async def put(self, path: str, json: dict | None = None) -> dict | list:
        return await self._request("PUT", path, json=json)

    async def patch(self, path: str, json: dict | None = None) -> dict | list:
        return await self._request("PATCH", path, json=json)

    async def delete(self, path: str, json: dict | None = None) -> dict | list:
        return await self._request("DELETE", path, json=json)
```

## Notas de Implementação

- **Retry**: só ocorre em `httpx.TimeoutException`, `httpx.RequestError` genérico (falha de conexão/DNS) e status `502`/`503`/`504`. Qualquer outro erro `4xx`/`5xx` é levantado imediatamente via `HTTPException`, sem retry.
- **Backoff**: fixo em `(1, 2, 4)` segundos entre tentativas — 4 tentativas no total (a inicial + 3 retries). Não é configurável por instância; é o mesmo padrão de `_BACKOFF` em `exchange_service.py`.
- **JSON malformado**: se a resposta tiver status de sucesso mas corpo não for JSON válido, vira `HTTPException(502)` em vez de propagar `ValueError` cru.
- **Logging**: toda tentativa falha gera `logger.warning`; falha definitiva (erro final ou esgotamento de tentativas) gera `logger.error`.
