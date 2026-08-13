from app.models.currency import Currency
from app.repositories.currency_repository import CurrencyRepository


class CurrencyService:
    def __init__(self, repository: CurrencyRepository):
        self.repository = repository

    async def list_active(self) -> list[Currency]:
        return await self.repository.find_all_active()
