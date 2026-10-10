from decimal import Decimal

from app.core.errors import FonteIndisponivel
from app.services.indicadores import ItemSerie, ResultadoMes, TotaisMes, calcular_serie


def mes_com_dados(mes: str, valor: str, beneficiarios: int) -> ResultadoMes:
    return ResultadoMes(mes=mes, totais=TotaisMes(valor=Decimal(valor), beneficiarios=beneficiarios))


def test_serie_calcula_valor_medio_e_variacao_entre_meses_seguidos():
    resultados = [
        mes_com_dados("2024-01", "1000.00", 100),
        mes_com_dados("2024-02", "1100.00", 110),
        mes_com_dados("2024-03", "1050.00", 105),
        mes_com_dados("2024-04", "1050.00", 105),
    ]

    assert calcular_serie(resultados) == [
        ItemSerie("2024-01", "disponivel", Decimal("1000.00"), 100, Decimal("10.00"), None),
        ItemSerie("2024-02", "disponivel", Decimal("1100.00"), 110, Decimal("10.00"), 10),
        ItemSerie("2024-03", "disponivel", Decimal("1050.00"), 105, Decimal("10.00"), -5),
        ItemSerie("2024-04", "disponivel", Decimal("1050.00"), 105, Decimal("10.00"), 0),
    ]


def test_serie_mantem_meses_sem_dado_com_nulos_e_nao_calcula_variacao_atravessando_lacuna():
    falha = FonteIndisponivel()
    resultados = [
        mes_com_dados("2023-10", "1000.00", 100),
        ResultadoMes("2023-11"),
        mes_com_dados("2023-12", "1200.00", 120),
        ResultadoMes("2024-01", erro=falha),
        mes_com_dados("2024-02", "0.00", 0),
    ]

    assert calcular_serie(resultados) == [
        ItemSerie("2023-10", "disponivel", Decimal("1000.00"), 100, Decimal("10.00"), None),
        ItemSerie("2023-11", "sem_dados", None, None, None, None),
        ItemSerie("2023-12", "disponivel", Decimal("1200.00"), 120, Decimal("10.00"), None),
        ItemSerie("2024-01", "fonte_indisponivel", None, None, None, None),
        ItemSerie("2024-02", "disponivel", Decimal("0.00"), 0, None, None),
    ]
