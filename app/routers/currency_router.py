from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.repositories.currency_repository import CurrencyRepository
from app.schemas.currency import CurrencyResponse
from app.services.currency_service import CurrencyService

router = APIRouter(prefix="/v1/currencies", tags=["Currency"])


@router.get("", response_model=list[CurrencyResponse])
async def list_currencies(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = CurrencyService(CurrencyRepository(db))
    return await service.list_active()
