from pydantic import BaseModel


class ExchangeResponse(BaseModel):
    name: str
    bid: float
    ask: float

    model_config = {"from_attributes": True}
