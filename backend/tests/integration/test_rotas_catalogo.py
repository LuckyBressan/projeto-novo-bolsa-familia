from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app


def test_periodos_seguem_configuracao():
    app.dependency_overrides[get_settings] = lambda: Settings(periodo_min="2023-11", periodo_max="2024-02")
    try:
        with TestClient(app) as cliente:
            corpo = cliente.get("/api/v1/periodos").json()
    finally:
        app.dependency_overrides.clear()

    assert corpo == {
        "periodo_min": "2023-11",
        "periodo_max": "2024-02",
        "max_meses_intervalo": 3,
        "anos": [{"ano": 2023, "meses": [11, 12]}, {"ano": 2024, "meses": [1, 2]}],
    }


def test_municipios_da_uf_informada_sem_diferenciar_maiusculas():
    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/municipios", params={"uf": "pr"})

    assert resposta.status_code == 200
    assert resposta.json() == {"items": [{"codigo_ibge": "4106902", "nome": "Curitiba", "uf": "PR"}], "total": 1}


def test_municipios_uf_inexistente_responde_estado_invalido():
    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/municipios", params={"uf": "YY"})

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "ESTADO_INVALIDO"
    assert resposta.json()["erro"]["detalhes"] == {"uf": "YY"}
