import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

PASTA_EXEMPLOS = Path(__file__).resolve().parents[2] / "app" / "data" / "mock" / "api-v1"


@pytest.mark.parametrize(
    ("rota", "arquivo"),
    [
        ("/api/v1/municipios?uf=PR", "municipios_uf-SC.json"),
        (
            "/api/v1/municipios/4202404/indicadores?ano=2024&mes_inicio=1&mes_fim=3",
            "indicadores_4214805_2024-01a03.json",
        ),
        (
            "/api/v1/capitais/comparacao?codigo_ibge_referencia=4202404&ano=2024&mes_inicio=4&mes_fim=6"
            "&metrica=valor_medio_por_beneficiario",
            "capitais_ref-4214805_2024-01a03_SC-PR-RS_valor-medio.json",
        ),
    ],
)
def test_parametro_fora_exemplos_devolve_exemplo_sucesso_mais_proximo(rota, arquivo):
    esperado = json.loads((PASTA_EXEMPLOS / arquivo).read_text(encoding="utf-8"))

    resposta = TestClient(app).get(rota)

    assert resposta.status_code == 200
    assert resposta.json() == esperado
