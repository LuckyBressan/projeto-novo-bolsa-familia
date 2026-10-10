import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.dependencias import get_fonte_dados
from app.core.errors import FonteIndisponivel
from app.main import app

PASTA_EXEMPLOS = Path(__file__).resolve().parents[2] / "app" / "data" / "mock" / "api-v1"


def exemplo(arquivo: str) -> dict:
    return json.loads((PASTA_EXEMPLOS / arquivo).read_text(encoding="utf-8"))


def test_evolucao_devolve_serie_da_cidade_a_depois_b():
    esperado = exemplo("evolucao_4202404-x-4209102_2023-10a12_lacuna.json")
    parametros = {"codigo_ibge_a": "4209102", "codigo_ibge_b": "4202404", "ano": 2023, "mes_inicio": 10, "mes_fim": 12}

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/evolucao-mensal", params=parametros)

    assert resposta.status_code == 200
    assert resposta.json() == {**esperado, "series": list(reversed(esperado["series"]))}


def test_evolucao_mesma_cidade_responde_parametro_invalido():
    parametros = {"codigo_ibge_a": "4214805", "codigo_ibge_b": "4214805", "ano": 2024, "mes_inicio": 1}

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/evolucao-mensal", params=parametros)

    assert resposta.status_code == 422
    assert resposta.json()["erro"]["codigo"] == "PARAMETRO_INVALIDO"
    assert resposta.json()["erro"]["detalhes"] == {"campos": ["codigo_ibge_a", "codigo_ibge_b"]}


class FonteFalhaMeses:
    def __init__(self, meses_com_falha: set[str]):
        self._meses_com_falha = meses_com_falha

    async def buscar(self, codigo_ibge: str, mes: str):
        if mes in self._meses_com_falha:
            raise FonteIndisponivel()
        return []


@pytest.mark.parametrize(
    ("meses_com_falha", "status"),
    [({"2024-01", "2024-02"}, 503), ({"2024-01"}, 200)],
    ids=["todos-meses-falham", "um-mes-falha-nas-duas-cidades"],
)
def test_evolucao_so_responde_fonte_indisponivel_quando_todos_meses_falham(meses_com_falha, status):
    parametros = {"codigo_ibge_a": "4214805", "codigo_ibge_b": "4202404", "ano": 2024, "mes_inicio": 1, "mes_fim": 2}

    with TestClient(app) as cliente:
        app.dependency_overrides[get_fonte_dados] = lambda: FonteFalhaMeses(meses_com_falha)
        try:
            resposta = cliente.get("/api/v1/evolucao-mensal", params=parametros)
        finally:
            app.dependency_overrides.clear()

    assert resposta.status_code == status
