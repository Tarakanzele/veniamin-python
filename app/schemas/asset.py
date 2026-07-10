from pydantic import BaseModel


class AssetCreate(BaseModel):
    ticker: str
    name: str
    market: str
    currency: str


class AssetUpdate(BaseModel):
    name: str | None = None
    market: str | None = None
    currency: str | None = None


class AssetResponse(BaseModel):
    id: int
    ticker: str
    name: str
    market: str
    currency: str

    model_config = {"from_attributes": True}
