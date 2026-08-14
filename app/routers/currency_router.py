from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas.currency import CurrencyResponse
from app.services.currency_service import CurrencyService

router = APIRouter(prefix="/v1/currencies", tags=["Currency"])


@router.get("", response_model=list[CurrencyResponse])
async def list_currencies(current_user: dict = Depends(get_current_user)):
    service = CurrencyService()
    return await service.list_activate()
