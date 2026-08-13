from app.schemas.exchange import ExchangeResponse


class ExchangeService:
    async def list_all(self) -> list[ExchangeResponse]:
        raise NotImplementedError

    async def sync(self) -> None:
        raise NotImplementedError
