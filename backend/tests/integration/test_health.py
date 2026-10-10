import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


@pytest.mark.parametrize("modo_mock", [True, False])
def test_health_informa_servico_ativo_e_modo_mock(modo_mock):
    app.dependency_overrides[get_settings] = lambda: Settings(modo_mock=modo_mock)
    try:
        resposta = TestClient(app).get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "service": "backend", "modo_mock": modo_mock}
