import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Synchronous test client"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_texts():
    """Sample texts for testing classification."""
    return {
        "left": "Universal healthcare is a human right. We must expand social programs to help working families and reduce income inequality.",
        "right": "Lower taxes and less government regulation will boost economic growth and create jobs. We must protect traditional values.",
        "center": "The committee heard arguments from both sides before reaching a bipartisan compromise on the infrastructure bill.",
    }
