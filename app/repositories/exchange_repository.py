from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exchange import Exchange


class ExchangeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_all(self) -> list[Exchange]:
        result = await self.db.execute(select(Exchange))
        return list(result.scalars().all())

    async def find_by_name(self, name: str) -> Exchange | None:
        result = await self.db.execute(select(Exchange).where(Exchange.name == name))
        return result.scalar_one_or_none()

    async def upsert_by_name(self, name: str, bid: float, ask: float) -> Exchange:
        existing = await self.find_by_name(name)
        if existing:
            existing.bid = bid
            existing.ask = ask
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        exchange = Exchange(name=name, bid=bid, ask=ask)
        self.db.add(exchange)
        await self.db.commit()
        await self.db.refresh(exchange)
        return exchange
