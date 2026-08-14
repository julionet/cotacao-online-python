import asyncio
import logging
import uuid
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.currency import CurrencyResponse
from app.schemas.exchange import ExchangeResponse
from app.services.currency_service import CurrencyService

logger = logging.getLogger(__name__)

_BACKOFF = (1, 2, 4)


class ExchangeService:
    def __init__(self, currency_service: CurrencyService | None = None):
        self.currency_service = currency_service or CurrencyService()

    async def list_all(self) -> list[ExchangeResponse]:
        """Busca todas as cotações cadastradas no Airtable."""
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

    async def sync_all(self) -> dict:
        """Sincroniza todas as moedas ativas com suas cotações na AwesomeAPI e atualiza o Airtable.

        Returns:
            dict: { success, total_currencies, updated, created, failed, errors, timestamp }

        Raises:
            HTTPException: Se falhar ao conectar com currency_service ou Airtable
            ValueError: Dados malformados
        """
        logger.info("Starting currency sync...")
        errors: list[dict] = []

        try:
            currencies = await self.currency_service.list_activate()
        except Exception as exc:
            logger.critical("Failed to fetch active currencies: %s", exc)
            raise

        if not currencies:
            logger.warning("No active currencies found, sync completed with 0 currencies")
            return {
                "success": True,
                "total_currencies": 0,
                "updated": 0,
                "created": 0,
                "failed": 0,
                "errors": [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        total = len(currencies)
        logger.info("Found %d active currencies to sync", total)

        async def _process(currency: CurrencyResponse) -> dict:
            logger.info("Processing %s...", currency.name)
            try:
                quote = await self._fetch_awesome_api(currency.code, currency.codein)
                result = await self._sync_exchange(currency, quote)
                return {"action": result["action"]}
            except Exception as exc:
                logger.error("Failed to sync %s: %s", currency.name, exc)
                return {
                    "error": {
                        "currency": currency.name,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                }

        results = await asyncio.gather(*[_process(c) for c in currencies])

        updated = sum(1 for r in results if r.get("action") == "updated")
        created = sum(1 for r in results if r.get("action") == "created")
        errors = [r["error"] for r in results if "error" in r]
        failed = len(errors)

        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info("Sync completed: %d updated, %d created, %d failed", updated, created, failed)
        if errors:
            logger.error("Sync errors: %s", errors)

        return {
            "success": failed == 0,
            "total_currencies": total,
            "updated": updated,
            "created": created,
            "failed": failed,
            "errors": errors,
            "timestamp": timestamp,
        }

    async def _fetch_awesome_api(self, code: str, codein: str) -> dict:
        """Busca cotação na AwesomeAPI para um par específico.

        Args:
            code: Moeda origem (ex: "USD")
            codein: Moeda destino (ex: "BRL")

        Returns:
            dict com bid, ask, varBid, pctChange, create_date

        Raises:
            HTTPException: Erro na requisição
            ValueError: Resposta malformada
        """
        url = f"{settings.EXCHANGE_API_BASE_URL}/json/last/{code.lower()}-{codein.lower()}"
        last_exc: Exception | None = None
        data: dict = {}

        for attempt in range(len(_BACKOFF) + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.EXCHANGE_API_TIMEOUT) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    break
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                error_msg = f"AwesomeAPI error: {status_code} {exc.response.text}"
                logger.error(error_msg)
                last_exc = HTTPException(status_code=status_code, detail=error_msg)
            except httpx.TimeoutException:
                error_msg = "Request timeout: AwesomeAPI not responding"
                logger.error(error_msg)
                last_exc = HTTPException(status_code=504, detail=error_msg)
            except httpx.RequestError as exc:
                error_msg = f"Request error: {exc}"
                logger.error(error_msg)
                last_exc = HTTPException(status_code=500, detail=error_msg)
            except ValueError as exc:
                raise ValueError("Malformed AwesomeAPI response: Invalid JSON") from exc

            if attempt < len(_BACKOFF):
                delay = _BACKOFF[attempt]
                logger.info("AwesomeAPI attempt %d failed, retrying in %ds...", attempt + 1, delay)
                await asyncio.sleep(delay)
            else:
                raise last_exc  # type: ignore[misc]

        key = f"{code.upper()}{codein.upper()}"
        entry = data.get(key)
        if not entry:
            raise ValueError(f"AwesomeAPI response missing key '{key}'")

        missing = [f for f in ("bid", "ask", "varBid", "pctChange", "create_date") if f not in entry]
        if missing:
            raise ValueError(f"AwesomeAPI response missing required fields: {missing}")

        return {
            "bid": float(entry["bid"]),
            "ask": float(entry["ask"]),
            "varBid": float(entry["varBid"]),
            "pctChange": float(entry["pctChange"]),
            "create_date": entry["create_date"],
        }

    async def _sync_exchange(self, currency: CurrencyResponse, quote: dict) -> dict:
        """Sincroniza uma cotação no Airtable (POST ou PUT).

        Args:
            currency: Moeda com possível Exchange relacionado
            quote: Dados da cotação (bid, ask, varBid, pctChange, create_date)

        Returns:
            dict: { action: "created"|"updated", record_id, guid, success }

        Raises:
            HTTPException: Erro na requisição Airtable
            ValueError: Dados inválidos
        """
        self._require_airtable_config()

        fields_base = {
            "Bid": quote["bid"],
            "Ask": quote["ask"],
            "Variation": quote["varBid"],
            "Percent": quote["pctChange"],
            "Timestamp": quote["create_date"],
        }

        if currency.exchange:
            url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_EXCHANGE}/{currency.exchange}"
            result = await self._airtable_request("PUT", url, json={"fields": fields_base})
            logger.info("Updated exchange %s for currency %s", currency.exchange, currency.name)
            return {
                "action": "updated",
                "record_id": result.get("id", currency.exchange),
                "guid": result.get("fields", {}).get("Guid"),
                "success": True,
            }

        guid = str(uuid.uuid4())
        url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_EXCHANGE}"
        payload = {"fields": {**fields_base, "Guid": guid, "Currency": [currency.id]}}
        result = await self._airtable_request("POST", url, json=payload)
        new_id = result.get("id")
        logger.info("Created exchange %s for currency %s", new_id, currency.name)
        return {
            "action": "created",
            "record_id": new_id,
            "guid": guid,
            "success": True,
        }

    async def _airtable_request(self, method: str, url: str, json: dict | None = None) -> dict:
        headers = {
            "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}",
            "Content-Type": "application/json",
        }
        last_exc: Exception | None = None
        response: httpx.Response | None = None

        for attempt in range(len(_BACKOFF) + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.AIRTABLE_TIMEOUT) as client:
                    response = await client.request(method, url, headers=headers, json=json)
                    response.raise_for_status()
                    break
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
                last_exc = HTTPException(status_code=status_code, detail=error_msg)
            except httpx.TimeoutException:
                error_msg = "Request timeout: Airtable API not responding"
                logger.error(error_msg)
                last_exc = HTTPException(status_code=504, detail=error_msg)
            except httpx.RequestError as exc:
                error_msg = f"Request error: {exc}"
                logger.error(error_msg)
                last_exc = HTTPException(status_code=500, detail=error_msg)

            if attempt < len(_BACKOFF):
                delay = _BACKOFF[attempt]
                logger.info("Airtable request attempt %d failed, retrying in %ds...", attempt + 1, delay)
                await asyncio.sleep(delay)
            else:
                raise last_exc  # type: ignore[misc]

        try:
            return response.json()  # type: ignore[union-attr]
        except ValueError as exc:
            error_msg = "Malformed Airtable response: Invalid JSON"
            logger.error(error_msg)
            raise ValueError(error_msg) from exc

    @staticmethod
    def _require_airtable_config() -> None:
        if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_URL:
            logger.critical("Missing critical config: AIRTABLE_TOKEN/AIRTABLE_BASE_URL")
            raise ValueError("Missing environment variables: AIRTABLE_TOKEN and AIRTABLE_BASE_URL")
