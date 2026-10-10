from decimal import Decimal

import pytest

from scripts.conferir_amostra import (
    Caso,
    Leitura,
    Linha,
    comparar,
    ler_api,
    ler_casos,
    ler_portal,
    montar_planilha,
)


def registro(valor: str, beneficiados: int) -> dict:
    return {"dataReferencia": "2024-01-01", "valor": Decimal(valor), "quantidadeBeneficiados": beneficiados}


@pytest.mark.parametrize(
    ("registros", "leitura"),
    [
        ([registro("1043055.00", 1525)], Leitura("disponivel", Decimal("1043055.00"), Decimal(1525), Decimal("683.97"))),
        (
            [registro("100.10", 2), registro("50.15", 1)],
            Leitura("disponivel", Decimal("150.25"), Decimal(3), Decimal("50.08")),
        ),
        ([registro("10.05", 2)], Leitura("disponivel", Decimal("10.05"), Decimal(2), Decimal("5.03"))),
        ([], Leitura("sem_dados")),
    ],
)
def test_leitura_do_portal_soma_registros_do_mes_e_calcula_valor_medio(registros, leitura):
    assert ler_portal(registros) == leitura


def corpo_api(status_dado: str, valor_total=None, beneficiarios=None, valor_medio=None) -> dict:
    return {
        "indicadores": {
            "status_dado": status_dado,
            "valor_total": valor_total,
            "beneficiarios_media_mensal": beneficiarios,
            "valor_medio_por_beneficiario": valor_medio,
        }
    }


@pytest.mark.parametrize(
    ("http_status", "corpo", "leitura"),
    [
        (
            200,
            corpo_api("disponivel", Decimal("1043055.0"), Decimal("1525.0"), Decimal("683.97")),
            Leitura("disponivel", Decimal("1043055.00"), Decimal(1525), Decimal("683.97")),
        ),
        (200, corpo_api("sem_dados"), Leitura("sem_dados")),
        (200, corpo_api("fonte_indisponivel"), Leitura("falha")),
        (503, {"erro": {"codigo": "FONTE_INDISPONIVEL"}}, Leitura("falha")),
    ],
)
def test_leitura_da_api_interna_usa_indicadores_de_um_mes(http_status, corpo, leitura):
    assert ler_api(http_status, corpo) == leitura


DISPONIVEL = Leitura("disponivel", Decimal("1043055.00"), Decimal(1525), Decimal("683.97"))


@pytest.mark.parametrize(
    ("portal", "api", "resultado"),
    [
        (DISPONIVEL, Leitura("disponivel", Decimal("1043055.0"), Decimal("1525.0"), Decimal("683.97")), "ok"),
        (Leitura("sem_dados"), Leitura("sem_dados"), "ok"),
        (DISPONIVEL, Leitura("disponivel", Decimal("1043055.01"), Decimal(1525), Decimal("683.97")), "divergente"),
        (DISPONIVEL, Leitura("disponivel", Decimal("1043055.00"), Decimal(1526), Decimal("683.97")), "divergente"),
        (DISPONIVEL, Leitura("disponivel", Decimal("1043055.00"), Decimal(1525), Decimal("683.96")), "divergente"),
        (DISPONIVEL, Leitura("sem_dados"), "divergente"),
        (DISPONIVEL, Leitura("falha"), "nao_conferido"),
        (Leitura("falha"), DISPONIVEL, "nao_conferido"),
    ],
)
def test_comparacao_exige_valores_iguais_e_nao_confere_quando_uma_fonte_falha(portal, api, resultado):
    assert comparar(portal, api) == resultado


def test_casos_da_amostra_vem_de_planilha_com_ponto_e_virgula_ignorando_colunas_a_mais():
    planilha = "\n".join(
        [
            "codigo_ibge;municipio;uf;mes;resultado",
            "4214805;Rio do Sul;SC;2024-01;ok",
            "",
            "1302603;Manaus;AM;2023-03;",
        ]
    )

    assert ler_casos(planilha) == [
        Caso("4214805", "Rio do Sul", "SC", "2024-01"),
        Caso("1302603", "Manaus", "AM", "2023-03"),
    ]


def test_planilha_traz_as_duas_fontes_com_numeros_no_formato_brasileiro():
    linhas = [
        Linha(
            Caso("4214805", "Rio do Sul", "SC", "2024-01"),
            DISPONIVEL,
            Leitura("disponivel", Decimal("1043055.0"), Decimal("1525.0"), Decimal("683.97")),
            "ok",
        ),
        Linha(Caso("5101837", "Boa Esperança do Norte", "MT", "2023-03"), Leitura("sem_dados"), Leitura("sem_dados"), "ok"),
        Linha(Caso("1302603", "Manaus", "AM", "2023-03"), Leitura("falha"), DISPONIVEL, "nao_conferido"),
    ]

    assert montar_planilha(linhas).splitlines() == [
        "codigo_ibge;municipio;uf;mes;portal_situacao;portal_valor_total;portal_beneficiarios;portal_valor_medio"
        ";api_situacao;api_valor_total;api_beneficiarios;api_valor_medio;resultado",
        "4214805;Rio do Sul;SC;2024-01;disponivel;1043055,00;1525;683,97;disponivel;1043055,00;1525;683,97;ok",
        "5101837;Boa Esperança do Norte;MT;2023-03;sem_dados;;;;sem_dados;;;;ok",
        "1302603;Manaus;AM;2023-03;falha;;;;disponivel;1043055,00;1525;683,97;nao_conferido",
    ]
    assert ler_casos(montar_planilha(linhas)) == [linha.caso for linha in linhas]
