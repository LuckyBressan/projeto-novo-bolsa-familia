import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencias import get_fonte_dados
from app.core.errors import FonteIndisponivel
from app.main import app

ARQUIVO_GERADOR = Path(__file__).resolve().parents[2] / "app" / "data" / "mock" / "gerar_mock.py"


def carregar_gerador_mock():
    especificacao = importlib.util.spec_from_file_location("gerar_mock", ARQUIVO_GERADOR)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def test_capitais_calculadas_igual_gerador_mock_para_combinacao_fora_exemplos():
    esperado = carregar_gerador_mock().comparar_capitais(
        "4202404", 2024, 4, 6, ["SP", "RJ", "DF"], "beneficiarios_media_mensal"
    )
    parametros = {
        "codigo_ibge_referencia": "4202404",
        "ano": 2024,
        "mes_inicio": 4,
        "mes_fim": 6,
        "capitais": "SP,RJ,DF",
        "metrica": "beneficiarios_media_mensal",
    }

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/capitais/comparacao", params=parametros)

    assert resposta.status_code == 200
    assert resposta.json() == esperado


def test_metrica_fora_lista_responde_metrica_invalida():
    parametros = {"codigo_ibge_referencia": "4214805", "ano": 2024, "mes_inicio": 1, "metrica": "populacao"}

    with TestClient(app) as cliente:
        resposta = cliente.get("/api/v1/capitais/comparacao", params=parametros)

    assert resposta.status_code == 422
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "METRICA_INVALIDA"
    assert erro["detalhes"] == {
        "metrica": "populacao",
        "metricas_aceitas": ["valor_total", "beneficiarios_media_mensal", "valor_medio_por_beneficiario"],
    }


class FonteSempreFalha:
    async def buscar(self, codigo_ibge: str, mes: str):
        raise FonteIndisponivel()


def test_capitais_com_todas_entradas_falhando_responde_fonte_indisponivel():
    parametros = {"codigo_ibge_referencia": "4214805", "ano": 2024, "mes_inicio": 1, "capitais": "SC,PR"}

    with TestClient(app) as cliente:
        app.dependency_overrides[get_fonte_dados] = FonteSempreFalha
        try:
            resposta = cliente.get("/api/v1/capitais/comparacao", params=parametros)
        finally:
            app.dependency_overrides.clear()

    assert resposta.status_code == 503
    assert resposta.json()["erro"]["codigo"] == "FONTE_INDISPONIVEL"
