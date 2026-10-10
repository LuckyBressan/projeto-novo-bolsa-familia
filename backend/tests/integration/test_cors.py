import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.parametrize(
    ("origem", "liberada"),
    [("http://localhost:5173", True), ("http://outro-site.test", False)],
)
def test_cors_libera_somente_origens_configuradas(origem, liberada):
    with TestClient(app) as cliente:
        resposta = cliente.options(
            "/api/v1/estados",
            headers={"Origin": origem, "Access-Control-Request-Method": "GET"},
        )

    assert (resposta.headers.get("access-control-allow-origin") == origem) is liberada
