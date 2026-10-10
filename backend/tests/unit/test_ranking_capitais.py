from decimal import Decimal

import pytest

from app.services.capitais import EntradaRanking, posicao_referencia, ranquear
from app.services.catalogos import Municipio
from app.services.indicadores import Indicadores


def entrada(
    nome: str, status: str = "disponivel", valor_total: str | None = None, codigo: str = "0000000"
) -> EntradaRanking:
    valor = Decimal(valor_total) if valor_total is not None else None
    indicadores = Indicadores(status, 3, 3, valor, Decimal("100.00"), Decimal("10.00"))
    return EntradaRanking(municipio=Municipio(codigo, nome, "XX"), indicadores=indicadores, serie=[])


def test_ranking_ordena_disponiveis_pela_metrica_e_deixa_demais_no_fim_em_ordem_alfabetica():
    entradas = [
        entrada("Vitória", valor_total="500.00"),
        entrada("Boa Vista", "sem_dados"),
        entrada("Natal", valor_total="900.00"),
        entrada("Aracaju", "parcial", "999.00"),
        entrada("Belém", valor_total="500.00"),
        entrada("Macapá", "fonte_indisponivel"),
        entrada("Árvore", valor_total="500.00"),
    ]

    ranking = ranquear(entradas, "valor_total")

    assert [(item.municipio.nome, item.posicao_ranking) for item in ranking] == [
        ("Natal", 1),
        ("Árvore", 2),
        ("Belém", 3),
        ("Vitória", 4),
        ("Aracaju", None),
        ("Boa Vista", None),
        ("Macapá", None),
    ]


RANKING = ranquear(
    [
        entrada("Natal", valor_total="900.00", codigo="2408102"),
        entrada("Belém", valor_total="500.00", codigo="1501402"),
        entrada("Vitória", valor_total="500.00", codigo="3205309"),
        entrada("Boa Vista", "sem_dados", codigo="1400100"),
    ],
    "valor_total",
)


@pytest.mark.parametrize(
    ("referencia", "posicao"),
    [
        (entrada("Rio do Sul", valor_total="700.00", codigo="4214805"), 2),
        (entrada("Rio do Sul", valor_total="500.00", codigo="4214805"), 2),
        (entrada("Rio do Sul", valor_total="950.00", codigo="4214805"), 1),
        (entrada("Natal", valor_total="900.00", codigo="2408102"), 1),
        (entrada("Vitória", valor_total="500.00", codigo="3205309"), 2),
        (entrada("Rio do Sul", "parcial", "999.00", codigo="4214805"), None),
    ],
    ids=["entre-capitais", "empate", "maior-que-todas", "capital-natal", "capital-empatada", "referencia-parcial"],
)
def test_posicao_referencia_conta_capitais_com_metrica_maior(referencia, posicao):
    assert posicao_referencia(referencia, RANKING, "valor_total") == posicao
