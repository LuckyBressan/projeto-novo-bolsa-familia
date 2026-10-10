import pytest

from app.core.errors import PeriodoInvalido
from app.services.periodo import RegraPeriodo

REGRA = RegraPeriodo(periodo_min="2023-03", periodo_max="2026-08", max_meses_intervalo=3)


@pytest.mark.parametrize(
    ("ano", "mes_inicio", "mes_fim", "meses"),
    [
        (2024, 1, 3, ["2024-01", "2024-02", "2024-03"]),
        (2024, 2, None, ["2024-02"]),
        (2023, 3, 3, ["2023-03"]),
        (2026, 6, 8, ["2026-06", "2026-07", "2026-08"]),
    ],
)
def test_periodo_valido_expande_meses(ano, mes_inicio, mes_fim, meses):
    periodo = REGRA.validar(ano, mes_inicio, mes_fim)

    assert periodo.meses == meses
    assert (periodo.ano, periodo.mes_inicio, periodo.mes_fim) == (ano, mes_inicio, mes_fim or mes_inicio)


FAIXA = ("O período deve estar entre 2023-03 e 2026-08.", {"periodo_min": "2023-03", "periodo_max": "2026-08"})
INTERVALO = ("O intervalo deve ter no máximo 3 meses, dentro do mesmo ano.", {"max_meses_intervalo": 3})


@pytest.mark.parametrize(
    ("ano", "mes_inicio", "mes_fim", "esperado"),
    [
        (2023, 1, 2, FAIXA),
        (2023, 2, 3, FAIXA),
        (2026, 8, 9, FAIXA),
        (2022, 5, 5, FAIXA),
        (2024, 1, 4, INTERVALO),
        (2024, 1, 6, INTERVALO),
        (
            2024,
            5,
            3,
            ("O mês inicial deve ser anterior ou igual ao mês final.", {"mes_inicio": 5, "mes_fim": 3}),
        ),
    ],
)
def test_periodo_invalido_indica_motivo(ano, mes_inicio, mes_fim, esperado):
    with pytest.raises(PeriodoInvalido) as erro:
        REGRA.validar(ano, mes_inicio, mes_fim)

    assert (erro.value.mensagem, erro.value.detalhes) == esperado
