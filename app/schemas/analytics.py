from pydantic import BaseModel


class AssetAnalyticsResponse(BaseModel):
    ticker: str
    current_price: float
    min_price: float
    max_price: float
    avg_price: float
    price_change: float
    price_change_pct: float
    data_points: int
