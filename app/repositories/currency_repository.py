from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.currency import Currency


class CurrencyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all_active(self) -> list[Currency]:
        result = await self.db.execute(select(Currency).where(Currency.is_active.is_(True)))
        return list(result.scalars().all())

    async def find_by_name(self, name: str) -> Currency | None:
        result = await self.db.execute(select(Currency).where(Currency.name == name))
        return result.scalar_one_or_none()

    async def create(self, currency: Currency) -> Currency:
        self.db.add(currency)
        await self.db.commit()
        await self.db.refresh(currency)
        return currency
