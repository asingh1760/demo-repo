

import os
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Use the API key from environment variable or fallback
API_KEY = os.getenv("API_KEY", "CG-5tut4FcZjyF6hsWidKxHHXrG")
headers = {"X-API-Key": API_KEY}

def test_list_coins():
    response = client.get("/v1/coins", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Default pagination returns up to 10 items
    assert len(data) <= 10

def test_list_categories():
    response = client.get("/v1/categories", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that pagination returns no more than 10 items
    assert len(data) <= 10

def test_get_coin_not_found():
    response = client.get("/v1/coins/nonexistentcoin", headers=headers)
    assert response.status_code == 404

def test_health_check():
    response = client.get("/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"

def test_version_info():
    response = client.get("/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)