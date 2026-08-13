from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.exchange_repository import ExchangeRepository
from app.schemas.exchange import ExchangeResponse
from app.services.exchange_service import ExchangeService

router = APIRouter(prefix="/v1/exchanges", tags=["Exchange"])


@router.get("", response_model=list[ExchangeResponse])
async def list_exchanges(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = ExchangeService(ExchangeRepository(db))
    return await service.list_all()


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_exchanges(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = ExchangeService(ExchangeRepository(db))
    await service.sync()
    return None
