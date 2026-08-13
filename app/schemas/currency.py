from datetime import datetime

from pydantic import BaseModel


class CurrencyResponse(BaseModel):
    id: str
    name: str
    code: str
    codein: str
    last_date: datetime
    exchange: str | None = None

    model_config = {"from_attributes": True}
