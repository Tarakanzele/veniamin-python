from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.dependencies import get_current_user
from app.core.exceptions import AssetNotFoundError
from app.db.session import get_session
from app.models.user import User
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.schemas.analytics import AssetAnalyticsResponse
from app.services.analytics_service import AnalyticsService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analytics", tags=["analytics"])


def get_analytics_service(session: AsyncSession = Depends(get_session)) -> AnalyticsService:
    return AnalyticsService(AssetRepository(session), PriceHistoryRepository(session))


@router.get("/{ticker}", response_model=AssetAnalyticsResponse)
async def get_asset_analytics(
    ticker: str,
    # ge=2 — минимум 2 точки данных, иначе нельзя посчитать изменение
    limit: int = Query(default=100, ge=2, le=1000),
    service: AnalyticsService = Depends(get_analytics_service),
    _: User = Depends(get_current_user),
) -> AssetAnalyticsResponse:
    try:
        # Сервис возвращает готовую Pydantic-схему — не ORM-объект
        return await service.get_asset_analytics(ticker, limit)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
