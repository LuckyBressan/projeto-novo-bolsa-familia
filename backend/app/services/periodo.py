from dataclasses import dataclass

from app.core.errors import PeriodoInvalido


@dataclass(frozen=True)
class Periodo:
    ano: int
    mes_inicio: int
    mes_fim: int

    @property
    def meses(self) -> list[str]:
        return [f"{self.ano:04d}-{mes:02d}" for mes in range(self.mes_inicio, self.mes_fim + 1)]


@dataclass(frozen=True)
class RegraPeriodo:
    periodo_min: str
    periodo_max: str
    max_meses_intervalo: int

    def anos_disponiveis(self) -> dict[int, list[int]]:
        anos: dict[int, list[int]] = {}
        ano, mes = map(int, self.periodo_min.split("-"))
        while f"{ano:04d}-{mes:02d}" <= self.periodo_max:
            anos.setdefault(ano, []).append(mes)
            ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
        return anos

    def validar(self, ano: int, mes_inicio: int, mes_fim: int | None) -> Periodo:
        periodo = Periodo(ano, mes_inicio, mes_fim if mes_fim is not None else mes_inicio)
        if periodo.mes_inicio > periodo.mes_fim:
            raise PeriodoInvalido(
                "O mês inicial deve ser anterior ou igual ao mês final.",
                {"mes_inicio": periodo.mes_inicio, "mes_fim": periodo.mes_fim},
            )
        if len(periodo.meses) > self.max_meses_intervalo:
            raise PeriodoInvalido(
                f"O intervalo deve ter no máximo {self.max_meses_intervalo} meses, dentro do mesmo ano.",
                {"max_meses_intervalo": self.max_meses_intervalo},
            )
        if periodo.meses[0] < self.periodo_min or periodo.meses[-1] > self.periodo_max:
            raise PeriodoInvalido(
                f"O período deve estar entre {self.periodo_min} e {self.periodo_max}.",
                {"periodo_min": self.periodo_min, "periodo_max": self.periodo_max},
            )
        return periodo
