from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.dependencies import get_current_user
from app.db.session import get_session
from app.core.exceptions import AlertNotFoundError
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.repositories.notification_history_repository import NotificationHistoryRepository
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate
from app.schemas.notification_history import NotificationHistoryResponse
from app.services.alert_service import AlertService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(session: AsyncSession = Depends(get_session)) -> AlertService:
    return AlertService(AlertRepository(session))


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_user),
) -> list[AlertResponse]:
    alerts = await service.get_user_alerts(current_user.id)
    return [AlertResponse.model_validate(a) for a in alerts]


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    body: AlertCreate,
    service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    alert = await service.create(current_user.id, body.asset_id, body.condition, body.value)
    return AlertResponse.model_validate(alert)


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    body: AlertUpdate,
    service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_user),
) -> AlertResponse:
    try:
        alert = await service.set_enabled(alert_id, current_user.id, body.enabled)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    service: AlertService = Depends(get_alert_service),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        await service.delete(alert_id, current_user.id)
    except AlertNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/notifications", response_model=list[NotificationHistoryResponse])
async def get_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[NotificationHistoryResponse]:
    repo = NotificationHistoryRepository(session)
    records = await repo.get_by_user(current_user.id, limit)
    return [NotificationHistoryResponse.model_validate(r) for r in records]
