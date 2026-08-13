from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_user
from app.schemas.exchange import ExchangeResponse
from app.services.exchange_service import ExchangeService

router = APIRouter(prefix="/v1/exchanges", tags=["Exchange"])


@router.get("", response_model=list[ExchangeResponse])
async def list_exchanges(current_user: dict = Depends(get_current_user)):
    service = ExchangeService()
    return await service.list_all()


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_exchanges(current_user: dict = Depends(get_current_user)):
    service = ExchangeService()
    await service.sync()
    return None
