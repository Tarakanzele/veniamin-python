from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.dependencies import get_current_user
from app.core.exceptions import AssetNotFoundError
from app.db.session import get_session
from app.models.user import User
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_history_repository import PriceHistoryRepository
from app.schemas.price_history import PriceHistoryCreate, PriceHistoryResponse
from app.services.price_history_service import PriceHistoryService
from sqlalchemy.ext.asyncio import AsyncSession

# Префикс /assets — история цен является суб-ресурсом актива
router = APIRouter(prefix="/assets", tags=["prices"])


def get_price_service(session: AsyncSession = Depends(get_session)) -> PriceHistoryService:
    # Сервис требует два репозитория — создаём оба с одной и той же сессией
    return PriceHistoryService(AssetRepository(session), PriceHistoryRepository(session))


@router.get("/{ticker}/prices", response_model=list[PriceHistoryResponse])
async def get_price_history(
    ticker: str,
    # Query параметр с ограничениями: минимум 1, максимум 1000 записей
    limit: int = Query(default=100, ge=1, le=1000),
    service: PriceHistoryService = Depends(get_price_service),
    _: User = Depends(get_current_user),
) -> list[PriceHistoryResponse]:
    try:
        records = await service.get_history(ticker, limit)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return [PriceHistoryResponse.model_validate(r) for r in records]


@router.post("/{ticker}/prices", response_model=PriceHistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_price(
    ticker: str,
    body: PriceHistoryCreate,  # тело содержит только поле price
    service: PriceHistoryService = Depends(get_price_service),
    _: User = Depends(get_current_user),
) -> PriceHistoryResponse:
    try:
        record = await service.add_price(ticker, body.price)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return PriceHistoryResponse.model_validate(record)
