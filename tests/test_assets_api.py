import pytest
from httpx import AsyncClient


async def auth_headers(client: AsyncClient) -> dict:
    await client.post("/api/v1/auth/register", json={"email": "u@test.com", "password": "pass"})
    r = await client.post("/api/v1/auth/login", json={"email": "u@test.com", "password": "pass"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.asyncio
async def test_create_asset(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    r = await client.post("/api/v1/assets/", json={"ticker": "aapl", "name": "Apple", "market": "NASDAQ", "currency": "usd"}, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data["ticker"] == "AAPL"
    assert data["currency"] == "USD"


@pytest.mark.asyncio
async def test_list_assets(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    await client.post("/api/v1/assets/", json={"ticker": "TSLA", "name": "Tesla", "market": "NASDAQ", "currency": "USD"}, headers=headers)
    r = await client.get("/api/v1/assets/", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


@pytest.mark.asyncio
async def test_get_asset(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    await client.post("/api/v1/assets/", json={"ticker": "TSLA", "name": "Tesla", "market": "NASDAQ", "currency": "USD"}, headers=headers)
    r = await client.get("/api/v1/assets/tsla", headers=headers)
    assert r.status_code == 200
    assert r.json()["ticker"] == "TSLA"


@pytest.mark.asyncio
async def test_get_asset_not_found(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    r = await client.get("/api/v1/assets/GHOST", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_asset(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    await client.post("/api/v1/assets/", json={"ticker": "TSLA", "name": "Tesla", "market": "NASDAQ", "currency": "USD"}, headers=headers)
    r = await client.patch("/api/v1/assets/TSLA", json={"name": "Tesla Inc."}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Tesla Inc."


@pytest.mark.asyncio
async def test_delete_asset(client: AsyncClient) -> None:
    headers = await auth_headers(client)
    await client.post("/api/v1/assets/", json={"ticker": "TSLA", "name": "Tesla", "market": "NASDAQ", "currency": "USD"}, headers=headers)
    r = await client.delete("/api/v1/assets/TSLA", headers=headers)
    assert r.status_code == 204
