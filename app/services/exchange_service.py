import logging

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.currency import CurrencyResponse
from app.schemas.exchange import ExchangeResponse
from app.services.currency_service import CurrencyService

logger = logging.getLogger(__name__)


class ExchangeService:
    def __init__(self, currency_service: CurrencyService | None = None):
        self.currency_service = currency_service or CurrencyService()

    async def list_all(self) -> list[ExchangeResponse]:
        """Busca todas as cotações (bid/ask) cadastradas no Airtable.

        Returns:
            list[ExchangeResponse]: Lista de cotações sincronizadas

        Raises:
            HTTPException: Se falhar ao conectar com Airtable (status 4xx/5xx)
            ValueError: Se resposta Airtable estiver malformada
        """
        self._require_airtable_config()

        url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_EXCHANGE}"
        logger.info("Fetching exchanges from Airtable: %s", url)

        data = await self._airtable_request("GET", url)

        records = data.get("records")
        if not isinstance(records, list):
            error_msg = "Invalid Airtable response: 'records' must be a list"
            logger.error(error_msg)
            raise ValueError(error_msg)

        exchanges: list[ExchangeResponse] = []
        for record in records:
            fields = record.get("fields", {})
            try:
                exchanges.append(
                    ExchangeResponse(
                        name=fields.get("Name"),
                        bid=float(fields.get("Bid")),
                        ask=float(fields.get("Ask")),
                    )
                )
            except (TypeError, ValueError) as exc:
                logger.error("Error mapping record %s: %s", record.get("id"), exc)
                continue

        logger.info("Successfully fetched %d exchanges", len(exchanges))
        return exchanges

    async def sync(self) -> None:
        """Sincroniza cotações: busca moedas ativas, consulta a API de câmbio externa
        (AwesomeAPI) e grava/atualiza o registro correspondente no Airtable (Exchange).
        """
        currencies = await self.currency_service.list_active()
        if not currencies:
            logger.warning("No active currencies to sync")
            return

        quotes = await self._fetch_quotes(currencies)

        for currency in currencies:
            pair_key = f"{currency.code}{currency.codein}"
            quote = quotes.get(pair_key)
            if not quote:
                logger.warning("No quote found for pair %s, skipping", pair_key)
                continue

            try:
                bid = float(quote.get("bid"))
                ask = float(quote.get("ask"))
            except (TypeError, ValueError):
                logger.error("Invalid bid/ask for pair %s, skipping", pair_key)
                continue

            await self._sync_exchange(currency, bid, ask)

    async def _fetch_quotes(self, currencies: list[CurrencyResponse]) -> dict:
        pairs = ",".join(f"{currency.code}-{currency.codein}" for currency in currencies)
        url = f"{settings.EXCHANGE_API_BASE_URL}/json/last/{pairs}"

        logger.info("Fetching quotes from exchange API: %s", url)

        try:
            async with httpx.AsyncClient(timeout=settings.EXCHANGE_API_TIMEOUT) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            error_msg = f"Exchange API error: {status_code} {exc.response.text}"
            logger.error(error_msg)
            raise HTTPException(status_code=status_code, detail=error_msg) from exc
        except httpx.TimeoutException as exc:
            error_msg = "Request timeout: Exchange API not responding"
            logger.error(error_msg)
            raise HTTPException(status_code=504, detail=error_msg) from exc
        except httpx.RequestError as exc:
            error_msg = f"Request error: {exc}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg) from exc
        except ValueError as exc:
            error_msg = "Malformed exchange API response: Invalid JSON"
            logger.error(error_msg)
            raise ValueError(error_msg) from exc

    async def _sync_exchange(self, currency: CurrencyResponse, bid: float, ask: float) -> None:
        """Atualiza a cotação existente (PUT) ou cria uma nova (POST) no Airtable.

        Conforme docs/SPEC_EXCHANGE_SERVICE.md: se `currency.exchange` estiver
        presente, faz PUT em /Exchange/{id}; caso contrário, faz POST em /Exchange
        e vincula o novo registro criado de volta à currency (garante que a
        próxima sincronização já encontre o exchange existente).
        """
        self._require_airtable_config()

        payload = {"fields": {"Name": currency.name, "Bid": bid, "Ask": ask}}

        if currency.exchange:
            url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_EXCHANGE}/{currency.exchange}"
            await self._airtable_request("PUT", url, json=payload)
            return

        url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_EXCHANGE}"
        created = await self._airtable_request("POST", url, json=payload)
        new_exchange_id = created.get("id")
        if new_exchange_id:
            await self._link_currency_exchange(currency.id, new_exchange_id)

    async def _link_currency_exchange(self, currency_id: str, exchange_id: str) -> None:
        url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_CURRENCY}/{currency_id}"
        payload = {"fields": {"Exchange": [exchange_id]}}
        await self._airtable_request("PATCH", url, json=payload)

    async def _airtable_request(self, method: str, url: str, json: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=settings.AIRTABLE_TIMEOUT) as client:
                response = await client.request(method, url, headers=headers, json=json)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                error_msg = "Unauthorized: Invalid Airtable token"
                logger.warning(error_msg)
            elif status_code == 404:
                error_msg = "Not Found: Exchange record not accessible"
                logger.error(error_msg)
            else:
                error_msg = f"Airtable API error: {status_code} {exc.response.text}"
                logger.error(error_msg)
            raise HTTPException(status_code=status_code, detail=error_msg) from exc
        except httpx.TimeoutException as exc:
            error_msg = "Request timeout: Airtable API not responding"
            logger.error(error_msg)
            raise HTTPException(status_code=504, detail=error_msg) from exc
        except httpx.RequestError as exc:
            error_msg = f"Request error: {exc}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg) from exc

        try:
            return response.json()
        except ValueError as exc:
            error_msg = "Malformed Airtable response: Invalid JSON"
            logger.error(error_msg)
            raise ValueError(error_msg) from exc

    @staticmethod
    def _require_airtable_config() -> None:
        if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_URL:
            logger.critical("Missing critical config: AIRTABLE_TOKEN/AIRTABLE_BASE_URL")
            raise ValueError("Missing environment variables: AIRTABLE_TOKEN and AIRTABLE_BASE_URL")
