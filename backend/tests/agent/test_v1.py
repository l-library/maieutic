from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    """测试api/v1端点"""
    response = client.get("api/v1/")
    assert response.status_code == 200
    assert response.json()["llm test"]
