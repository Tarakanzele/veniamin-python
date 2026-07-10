import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient) -> None:
    r = await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "pass123"})
    assert r.status_code == 201
    assert r.json()["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient) -> None:
    payload = {"email": "a@b.com", "password": "pass123"}
    await client.post("/api/v1/auth/register", json=payload)
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_login(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "pass123"})
    r = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "pass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "pass123"})
    r = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "pass123"})
    login = await client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "pass123"})
    token = login.json()["access_token"]
    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient) -> None:
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 403
