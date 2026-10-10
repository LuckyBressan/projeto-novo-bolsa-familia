import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencias import get_fonte_dados
from app.core.errors import FonteIndisponivel
from app.main import app

PASTA_EXEMPLOS = Path(__file__).resolve().parents[2] / "app" / "data" / "mock" / "api-v1"


def exemplo(arquivo: str) -> dict:
    return json.loads((PASTA_EXEMPLOS / arquivo).read_text(encoding="utf-8"))


def test_indicadores_calculados_para_qualquer_municipio_e_periodo():
    blumenau = exemplo("comparacao_4202404-x-4209102_2023-10a12_parcial.json")["municipios"][0]

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/municipios/4202404/indicadores", params={"ano": 2023, "mes_inicio": 10, "mes_fim": 12})

    assert resposta.status_code == 200
    assert resposta.json() == {
        "fonte": "mock",
        "municipio": blumenau["municipio"],
        "periodo": {"ano": 2023, "mes_inicio": 10, "mes_fim": 12, "meses": ["2023-10", "2023-11", "2023-12"]},
        "indicadores": blumenau["indicadores"],
    }


def test_comparacao_devolve_cidade_a_depois_b():
    esperado = exemplo("comparacao_4202404-x-4209102_2023-10a12_parcial.json")
    parametros = {"codigo_ibge_a": "4209102", "codigo_ibge_b": "4202404", "ano": 2023, "mes_inicio": 10, "mes_fim": 12}

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/comparacoes/municipios", params=parametros)

    assert resposta.status_code == 200
    assert resposta.json() == {**esperado, "municipios": list(reversed(esperado["municipios"]))}


def test_comparacao_mesma_cidade_responde_parametro_invalido():
    parametros = {"codigo_ibge_a": "4214805", "codigo_ibge_b": "4214805", "ano": 2024, "mes_inicio": 1}

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/comparacoes/municipios", params=parametros)

    assert resposta.status_code == 422
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "PARAMETRO_INVALIDO"
    assert erro["mensagem"] == "As duas cidades devem ser diferentes."
    assert erro["detalhes"] == {"campos": ["codigo_ibge_a", "codigo_ibge_b"]}


class FonteSempreFalha:
    async def buscar(self, codigo_ibge: str, mes: str):
        raise FonteIndisponivel()


def test_comparacao_com_todas_entradas_falhando_responde_fonte_indisponivel():
    parametros = {"codigo_ibge_a": "4214805", "codigo_ibge_b": "4202404", "ano": 2024, "mes_inicio": 1}

    with TestClient(app) as cliente:
        app.dependency_overrides[get_fonte_dados] = FonteSempreFalha
        try:
            resposta = cliente.get("/api/v1/comparacoes/municipios", params=parametros)
        finally:
            app.dependency_overrides.clear()

    assert resposta.status_code == 503
    assert resposta.json()["erro"]["codigo"] == "FONTE_INDISPONIVEL"
