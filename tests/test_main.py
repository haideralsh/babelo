import pytest
from httpx import ASGITransport, AsyncClient

from bab.main import app


@pytest.mark.asyncio
async def test_root_returns_ok_status():
    """Test that the root endpoint returns a healthy status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Bab API"
