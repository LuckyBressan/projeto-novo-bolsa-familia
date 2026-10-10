from urllib.parse import parse_qs, urlsplit

import pytest

from scripts.simular_carga import (
    Consulta,
    Execucao,
    Resultado,
    Resumo,
    gerar_consultas,
    montar_relatorio,
    resumir,
)

CODIGOS = ["4214805", "4202404", "4209102", "3550308"]
MESES_ANO = {2023: [11, 12], 2024: [1, 2, 3, 4]}


def test_gera_quantidade_pedida_misturando_rotas_e_repete_com_mesma_semente():
    consultas = gerar_consultas(16, CODIGOS, MESES_ANO, semente=7)

    assert len(consultas) == 16
    assert {consulta.tipo for consulta in consultas} == {"indicadores", "comparacao", "evolucao", "capitais"}
    assert all(consulta.caminho.startswith("/api/v1/") for consulta in consultas)
    assert consultas == gerar_consultas(16, CODIGOS, MESES_ANO, semente=7)
    assert consultas != gerar_consultas(16, CODIGOS, MESES_ANO, semente=8)


def test_periodos_variam_de_um_a_tres_meses_seguidos_dentro_dos_meses_disponiveis():
    consultas = gerar_consultas(200, CODIGOS, MESES_ANO, semente=7)

    tamanhos = set()
    for consulta in consultas:
        parametros = {nome: int(valores[0]) for nome, valores in parse_qs(urlsplit(consulta.caminho).query).items()}
        meses = list(range(parametros["mes_inicio"], parametros["mes_fim"] + 1))
        assert set(meses) <= set(MESES_ANO[parametros["ano"]])
        tamanhos.add(len(meses))
    assert tamanhos == {1, 2, 3}


def resultado(http_status: int | None, segundos: float, codigo_erro: str | None = None) -> Resultado:
    return Resultado(Consulta("indicadores", "/api/v1/municipios/4214805/indicadores"), http_status, codigo_erro, segundos)


RESPOSTAS_NORMAIS = [
    resultado(200, 0.2),
    resultado(200, 0.4),
    resultado(200, 61.0),
    resultado(503, 0.3, "FONTE_INDISPONIVEL"),
    resultado(None, 5.0),
]


@pytest.mark.parametrize(
    ("extras", "amostras", "respostas", "erros_limite", "pico", "aprovado"),
    [
        ([], [0, 90, 150, 120], {"200": 3, "503": 1, "sem resposta": 1}, 0, 150, True),
        ([], [0, 151], {"200": 3, "503": 1, "sem resposta": 1}, 0, 151, False),
        ([resultado(503, 0.1, "LIMITE_FONTE_EXCEDIDO")], [10], {"200": 3, "503": 2, "sem resposta": 1}, 1, 10, False),
        ([resultado(429, 0.1)], [], {"200": 3, "429": 1, "503": 1, "sem resposta": 1}, 1, 0, False),
    ],
)
def test_resumo_conta_respostas_e_reprova_pico_acima_do_limite_ou_erro_de_limite(
    extras, amostras, respostas, erros_limite, pico, aprovado
):
    resumo = resumir(RESPOSTAS_NORMAIS + extras, amostras, limite_rpm=150)

    assert resumo == Resumo(
        consultas=5 + len(extras),
        respostas=respostas,
        erros_limite=erros_limite,
        tempo_mediano=resumo.tempo_mediano,
        tempo_maximo=61.0,
        pico_chamadas_minuto=pico,
        limite_rpm=150,
        aprovado=aprovado,
    )
    assert resumir(RESPOSTAS_NORMAIS, [], limite_rpm=150).tempo_mediano == 0.4


def test_relatorio_reune_resumo_amostras_consumo_e_tempo_de_cada_consulta():
    execucao = Execucao(
        resultados=[resultado(200, 0.25049), resultado(503, 0.5, "FONTE_INDISPONIVEL")],
        amostras=[0, 3],
        limite_rpm=150,
        consumo_final={"chamadas_desde_inicio": 3},
    )

    assert montar_relatorio(execucao) == {
        "resumo": {
            "consultas": 2,
            "respostas": {"200": 1, "503": 1},
            "erros_limite": 0,
            "tempo_mediano": 0.375,
            "tempo_maximo": 0.5,
            "pico_chamadas_minuto": 3,
            "limite_rpm": 150,
            "aprovado": True,
        },
        "amostras_chamadas_minuto": [0, 3],
        "consumo_final": {"chamadas_desde_inicio": 3},
        "consultas": [
            {
                "tipo": "indicadores",
                "caminho": "/api/v1/municipios/4214805/indicadores",
                "http_status": 200,
                "codigo_erro": None,
                "segundos": 0.25,
            },
            {
                "tipo": "indicadores",
                "caminho": "/api/v1/municipios/4214805/indicadores",
                "http_status": 503,
                "codigo_erro": "FONTE_INDISPONIVEL",
                "segundos": 0.5,
            },
        ],
    }
