import logging
from datetime import datetime

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.currency import CurrencyResponse

logger = logging.getLogger(__name__)


class CurrencyService:
    async def list_activate(self) -> list[CurrencyResponse]:
        """Busca todas as moedas ativas (Active == true) do Airtable.

        Returns:
            list[CurrencyResponse]: Lista de moedas configuradas e ativas

        Raises:
            HTTPException: Se falhar ao conectar com Airtable (status 4xx/5xx)
            ValueError: Se resposta Airtable estiver malformada
        """
        if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_URL:
            logger.critical("Missing critical config: AIRTABLE_TOKEN/AIRTABLE_BASE_URL")
            raise ValueError("Missing environment variables: AIRTABLE_TOKEN and AIRTABLE_BASE_URL")

        url = f"{settings.AIRTABLE_BASE_URL}/{settings.AIRTABLE_TABLE_CURRENCY}"
        headers = {
            "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}",
            "Content-Type": "application/json",
        }

        logger.info("Fetching active currencies from Airtable: %s", url)

        try:
            async with httpx.AsyncClient(timeout=settings.AIRTABLE_TIMEOUT) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                error_msg = "Unauthorized: Invalid Airtable token"
                logger.warning(error_msg)
            elif status_code == 404:
                error_msg = "Not Found: Currency table not accessible"
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
            data = response.json()
        except ValueError as exc:
            error_msg = "Malformed Airtable response: Invalid JSON"
            logger.error(error_msg)
            raise ValueError(error_msg) from exc

        if "records" not in data:
            error_msg = "Invalid Airtable response: 'records' field not found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        records = data.get("records")
        if not isinstance(records, list):
            error_msg = "Invalid Airtable response: 'records' must be a list"
            logger.error(error_msg)
            raise ValueError(error_msg)

        currencies: list[CurrencyResponse] = []

        for record in records:
            fields = record.get("fields", {})
            if not fields.get("Active", False):
                continue

            created_time_str = record.get("createdTime")
            if not created_time_str:
                logger.warning("Record %s missing createdTime, skipping", record.get("id"))
                continue

            try:
                last_date = datetime.fromisoformat(created_time_str.replace("Z", "+00:00"))
                exchange_list = fields.get("Exchange")
                exchange_id = exchange_list[0] if isinstance(exchange_list, list) and exchange_list else None
                max_variation = fields.get("Max")
                min_variation = fields.get("Min")
                currency = CurrencyResponse(
                    id=record.get("id"),
                    name=fields.get("Name"),
                    code=fields.get("Origin"),
                    codein=fields.get("Destiny"),
                    last_date=last_date,
                    exchange=exchange_id,
                    max_variation=float(max_variation) if max_variation is not None else None,
                    min_variation=float(min_variation) if min_variation is not None else None,
                )
            except (KeyError, ValueError, AttributeError) as exc:
                logger.error("Error mapping record %s: %s", record.get("id"), exc)
                continue

            currencies.append(currency)

        if not currencies:
            logger.warning("No active currencies found in Airtable")
        else:
            logger.info("Successfully fetched %d active currencies", len(currencies))

        return currencies
