from pydantic import BaseModel

from app.services.periodo import Periodo


class AnoMeses(BaseModel):
    ano: int
    meses: list[int]


class PeriodosResposta(BaseModel):
    periodo_min: str
    periodo_max: str
    max_meses_intervalo: int
    anos: list[AnoMeses]


class PeriodoResposta(BaseModel):
    ano: int
    mes_inicio: int
    mes_fim: int
    meses: list[str]

    @classmethod
    def criar(cls, periodo: Periodo) -> "PeriodoResposta":
        return cls(ano=periodo.ano, mes_inicio=periodo.mes_inicio, mes_fim=periodo.mes_fim, meses=periodo.meses)
