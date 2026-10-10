import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASTA_EXEMPLOS = Path(__file__).resolve().parents[2] / "app" / "data" / "mock" / "api-v1"
EXEMPLOS = json.loads((PASTA_EXEMPLOS / "_rotas.json").read_text(encoding="utf-8"))
CONTADORES_DIAGNOSTICO = (
    "chamadas_ultimo_minuto",
    "chamadas_desde_inicio",
    "chamadas_bloqueadas_pelo_limitador",
    "iniciado_em",
)
CONTADORES_CACHE = ("itens", "hits", "misses")


def sem_valores_variaveis(corpo: dict) -> dict:
    corpo = copy.deepcopy(corpo)
    if "erro" in corpo:
        corpo["erro"].pop("correlacao_id", None)
    if "limite_rpm_configurado" in corpo:
        for campo in CONTADORES_DIAGNOSTICO:
            corpo[campo] = type(corpo[campo]).__name__
        for campo in CONTADORES_CACHE:
            corpo["cache"][campo] = type(corpo["cache"][campo]).__name__
    return corpo


@pytest.mark.parametrize("exemplo", EXEMPLOS, ids=lambda exemplo: exemplo["arquivo"])
def test_rota_responde_igual_exemplo_mock(exemplo):
    esperado = json.loads((PASTA_EXEMPLOS / exemplo["arquivo"]).read_text(encoding="utf-8"))

    with TestClient(app) as cliente:
        resposta = cliente.get(exemplo["rota"])

    assert resposta.status_code == exemplo["http_status"]
    assert sem_valores_variaveis(resposta.json()) == sem_valores_variaveis(esperado)
