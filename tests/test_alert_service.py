from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import AlertNotFoundError
from app.models.alert import Alert, AlertCondition
from app.services.alert_service import AlertService


def make_alert(user_id: int = 1) -> Alert:
    return Alert(id=1, user_id=user_id, asset_id=1, condition=AlertCondition.ABOVE, value=200.0, enabled=True)


def make_service(alert: Alert | None = None) -> AlertService:
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=alert)
    repo.get_by_user = AsyncMock(return_value=[alert] if alert else [])
    repo.create = AsyncMock(return_value=make_alert())
    repo.set_enabled = AsyncMock(side_effect=lambda a, enabled: setattr(a, "enabled", enabled) or a)
    repo.delete = AsyncMock()
    return AlertService(repo)


@pytest.mark.asyncio
async def test_get_user_alerts() -> None:
    service = make_service(make_alert())
    alerts = await service.get_user_alerts(1)
    assert len(alerts) == 1


@pytest.mark.asyncio
async def test_create_alert() -> None:
    service = make_service()
    alert = await service.create(1, 1, AlertCondition.ABOVE, 200.0)
    assert alert.id == 1


@pytest.mark.asyncio
async def test_delete_not_owner_raises() -> None:
    alert = make_alert(user_id=2)
    service = make_service(alert)
    with pytest.raises(AlertNotFoundError):
        await service.delete(1, user_id=1)


@pytest.mark.asyncio
async def test_delete_not_found_raises() -> None:
    service = make_service(None)
    with pytest.raises(AlertNotFoundError):
        await service.delete(99, user_id=1)


@pytest.mark.asyncio
async def test_set_enabled_not_owner_raises() -> None:
    alert = make_alert(user_id=2)
    service = make_service(alert)
    with pytest.raises(AlertNotFoundError):
        await service.set_enabled(1, user_id=1, enabled=False)
