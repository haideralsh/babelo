import pytest
from httpx import ASGITransport, AsyncClient

from server.main import app


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
    assert data["service"] == "Babelo API"


@pytest.mark.asyncio
async def test_models_list_endpoint():
    """Test that the models list endpoint returns available models."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/model/list")

    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "default_model_id" in data
    assert data["default_model_id"] == "nllb"

    model_ids = [m["model_id"] for m in data["models"]]
    assert "nllb" in model_ids
    assert "translategemma" in model_ids


@pytest.mark.asyncio
async def test_languages_endpoint_default():
    """Test that languages endpoint returns NLLB languages by default."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/languages")

    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    assert "model_id" in data
    assert data["model_id"] == "nllb"
    assert "English" in data["languages"]


@pytest.mark.asyncio
async def test_languages_endpoint_with_model_id():
    """Test that languages endpoint respects model_id parameter."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/languages?model_id=translategemma")

    assert response.status_code == 200
    data = response.json()
    assert data["model_id"] == "translategemma"
    assert "English" in data["languages"]
    # TranslateGemma uses ISO codes
    assert data["languages"]["English"] == "en"


@pytest.mark.asyncio
async def test_languages_endpoint_invalid_model():
    """Test that languages endpoint returns error for invalid model_id."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/languages?model_id=invalid")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_model_status_endpoint():
    """Test that model status endpoint returns status."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/model/status")

    assert response.status_code == 200
    data = response.json()
    assert "model_id" in data
    assert "is_downloaded" in data
    assert "is_loaded" in data
