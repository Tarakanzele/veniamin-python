from datetime import datetime

from pydantic import BaseModel


class NotificationHistoryResponse(BaseModel):
    id: int
    user_id: int
    alert_id: int
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
