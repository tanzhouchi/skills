"""
健康检查集成测试。
"""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    """健康检查固定返回裸状态。"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
