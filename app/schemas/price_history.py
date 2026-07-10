from datetime import datetime

from pydantic import BaseModel


class PriceHistoryResponse(BaseModel):
    id: int
    asset_id: int
    price: float
    timestamp: datetime

    model_config = {"from_attributes": True}


class PriceHistoryCreate(BaseModel):
    price: float
