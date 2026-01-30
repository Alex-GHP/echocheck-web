import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from pymongo import AsyncMongoClient

from app.core.config import get_settings
from app.main import app
from app.services.database import database


@pytest.fixture
def client():
    """Synchronous test client"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client():
    """
    Asynchronous test client with database connection.
    Creates a fresh database connection for each test to avoid event loop issues.
    Uses a short timeout (2s) to fail fast when MongoDB is unavailable.
    """
    if database.client is not None:
        try:
            await database.disconnect()
        except Exception:  # noqa: BLE001, S110
            database.client = None
        database.client = None
        database.db = None

    try:
        settings = get_settings()
        database.client = AsyncMongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=2000,
        )
        database.db = database.client[settings.mongodb_db_name]
        await database.client.admin.command("ping")
    except Exception:  # noqa: BLE001, S110
        database.client = None
        database.db = None

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    try:
        await database.disconnect()
    except Exception:  # noqa: BLE001, S110
        database.db = None
    database.client = None
    database.db = None


@pytest.fixture
def sample_texts():
    """Sample texts for testing classification."""
    return {
        "left": "Universal healthcare is a human right. We must expand social programs to help working families and reduce income inequality.",
        "right": "Lower taxes and less government regulation will boost economic growth and create jobs. We must protect traditional values.",
        "center": "The committee heard arguments from both sides before reaching a bipartisan compromise on the infrastructure bill.",
    }
