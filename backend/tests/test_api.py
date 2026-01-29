def test_root_endpoint(client):
    """Test the root endpoint returns API info"""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "EchoCheck API"
    assert data["version"] == "1.0.0"
    assert "docs" in data
    assert "health" in data


def test_health_endpoint(client):
    """Test the health endpoint returns status"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert "model_name" in data


def test_docs_endpoint(client):
    """Test that OpenAPI docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
