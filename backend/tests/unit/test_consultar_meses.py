from decimal import Decimal

import pytest

from app.core.errors import FonteIndisponivel, RespostaFonteInvalida
from app.integrations.portal_transparencia import RegistroBeneficio
from app.services.indicadores import ResultadoMes, TotaisMes, consultar_meses

pytestmark = pytest.mark.anyio

REGISTRO = RegistroBeneficio("4214805", "RIO DO SUL", "SC", "2024-01", Decimal("1000.50"), 10, None, None)


class FonteFalsa:
    def __init__(self, respostas: dict):
        self._respostas = respostas

    async def buscar(self, codigo_ibge: str, mes: str):
        resposta = self._respostas[mes]
        if isinstance(resposta, Exception):
            raise resposta
        return resposta


async def test_cada_mes_vira_resultado_com_dados_sem_dados_ou_falha():
    falha = FonteIndisponivel()
    invalida = RespostaFonteInvalida()
    fonte = FonteFalsa({"2024-01": [REGISTRO], "2024-02": [], "2024-03": falha, "2024-04": invalida})

    resultados = await consultar_meses(fonte, "4214805", ["2024-01", "2024-02", "2024-03", "2024-04"])

    assert resultados == [
        ResultadoMes("2024-01", totais=TotaisMes(Decimal("1000.50"), 10)),
        ResultadoMes("2024-02"),
        ResultadoMes("2024-03", erro=falha),
        ResultadoMes("2024-04", erro=invalida),
    ]
