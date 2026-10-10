from decimal import Decimal

import pytest

from app.core.errors import FonteIndisponivel
from app.services.indicadores import Indicadores, ResultadoMes, TotaisMes, calcular_indicadores


def mes_com_dados(mes: str, valor: str, beneficiarios: int) -> ResultadoMes:
    return ResultadoMes(mes=mes, totais=TotaisMes(valor=Decimal(valor), beneficiarios=beneficiarios))


@pytest.mark.parametrize(
    ("resultados", "esperado"),
    [
        (
            [mes_com_dados("2024-02", "1023980.19", 1590)],
            Indicadores("disponivel", 1, 1, Decimal("1023980.19"), Decimal("1590.00"), Decimal("644.01")),
        ),
        (
            [
                mes_com_dados("2023-10", "3683071.26", 5736),
                ResultadoMes(mes="2023-11"),
                mes_com_dados("2023-12", "3747450.00", 5810),
            ],
            Indicadores("parcial", 3, 2, Decimal("7430521.26"), Decimal("5773.00"), Decimal("643.56")),
        ),
        (
            [
                mes_com_dados("2024-01", "1000.00", 1000),
                mes_com_dados("2024-02", "1000.00", 1001),
                mes_com_dados("2024-03", "1000.00", 1001),
            ],
            Indicadores("disponivel", 3, 3, Decimal("3000.00"), Decimal("1000.67"), Decimal("1.00")),
        ),
    ],
    ids=["um-mes", "parcial-exemplo-plano-05", "media-nao-exata"],
)
def test_cards_calculados_com_meses_disponiveis(resultados, esperado):
    assert calcular_indicadores(resultados) == esperado


@pytest.mark.parametrize(
    ("resultados", "esperado"),
    [
        (
            [ResultadoMes(mes="2024-01"), ResultadoMes(mes="2024-02")],
            Indicadores("sem_dados", 2, 0, None, None, None),
        ),
        (
            [mes_com_dados("2024-11", "1000.00", 10), ResultadoMes(mes="2024-12", erro=FonteIndisponivel())],
            Indicadores("fonte_indisponivel", 2, None, None, None, None),
        ),
    ],
    ids=["sem-dados", "fonte-indisponivel-em-um-mes"],
)
def test_cards_sem_valores_quando_nao_ha_dados_ou_fonte_falha(resultados, esperado):
    assert calcular_indicadores(resultados) == esperado


def test_valor_medio_nulo_quando_soma_beneficiarios_zero():
    indicadores = calcular_indicadores([mes_com_dados("2024-01", "0.00", 0)])

    assert indicadores == Indicadores("disponivel", 1, 1, Decimal("0.00"), Decimal("0.00"), None)
