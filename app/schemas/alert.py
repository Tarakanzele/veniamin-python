from pydantic import BaseModel

from app.models.alert import AlertCondition


class AlertCreate(BaseModel):
    asset_id: int
    condition: AlertCondition
    value: float


class AlertResponse(BaseModel):
    id: int
    user_id: int
    asset_id: int
    condition: AlertCondition
    value: float
    enabled: bool

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    enabled: bool
