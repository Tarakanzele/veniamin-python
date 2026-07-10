from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.security import hash_password
from app.models.user import User
from app.services.auth_service import AuthService


def make_service(user: User | None = None) -> AuthService:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=user)
    repo.create = AsyncMock(return_value=User(id=1, email="test@example.com", password_hash="x"))
    return AuthService(repo)


@pytest.mark.asyncio
async def test_register_success() -> None:
    service = make_service(user=None)
    user = await service.register("test@example.com", "password123")
    assert user.id == 1


@pytest.mark.asyncio
async def test_register_duplicate_raises() -> None:
    existing = User(id=1, email="test@example.com", password_hash="x")
    service = make_service(user=existing)
    with pytest.raises(UserAlreadyExistsError):
        await service.register("test@example.com", "password123")


@pytest.mark.asyncio
async def test_login_success() -> None:
    password = "password123"
    user = User(id=1, email="test@example.com", password_hash=hash_password(password))
    service = make_service(user=user)
    token = await service.login("test@example.com", password)
    assert token.access_token
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_raises() -> None:
    user = User(id=1, email="test@example.com", password_hash=hash_password("correct"))
    service = make_service(user=user)
    with pytest.raises(InvalidCredentialsError):
        await service.login("test@example.com", "wrong")


@pytest.mark.asyncio
async def test_login_unknown_email_raises() -> None:
    service = make_service(user=None)
    with pytest.raises(InvalidCredentialsError):
        await service.login("ghost@example.com", "password")
