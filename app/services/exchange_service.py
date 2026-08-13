import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.exchange import Exchange
from app.repositories.exchange_repository import ExchangeRepository


class ExchangeService:
    def __init__(self, repository: ExchangeRepository):
        self.repository = repository

    async def list_all(self) -> list[Exchange]:
        return await self.repository.find_all()

    async def sync(self) -> None:
        """Busca as cotações mais recentes na API externa e grava/atualiza em `exchanges`.

        Fonte padrão: AwesomeAPI (economia.awesomeapi.com.br). Os pares consultados
        são configurados via EXCHANGE_API_PAIRS (ex.: "USD-BRL,EUR-BRL").
        """
        url = f"{settings.EXCHANGE_API_BASE_URL}/json/last/{settings.EXCHANGE_API_PAIRS}"

        try:
            async with httpx.AsyncClient(timeout=settings.EXCHANGE_API_TIMEOUT) as client:
                try:
                    response = await client.get(url)
                except httpx.TimeoutException:
                    # uma única tentativa extra em caso de timeout
                    response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor",
            ) from exc

        for item in data.values():
            code = item.get("code")
            codein = item.get("codein")
            bid = item.get("bid")
            ask = item.get("ask")
            if not code or not codein or bid is None or ask is None:
                continue
            name = f"{code}-{codein}"
            await self.repository.upsert_by_name(name=name, bid=float(bid), ask=float(ask))
