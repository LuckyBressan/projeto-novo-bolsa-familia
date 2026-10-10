from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.indicadores import Indicadores

Fonte = Literal["portal_transparencia", "mock"]
StatusDado = Literal["disponivel", "parcial", "sem_dados", "fonte_indisponivel"]


def numero(valor: Decimal | None) -> float | None:
    return float(valor) if valor is not None else None


class IndicadoresResposta(BaseModel):
    status_dado: StatusDado
    meses_solicitados: int
    meses_com_dados: int | None
    valor_total: float | None
    beneficiarios_media_mensal: float | None
    valor_medio_por_beneficiario: float | None

    @classmethod
    def criar(cls, indicadores: Indicadores) -> "IndicadoresResposta":
        return cls(
            status_dado=indicadores.status_dado,
            meses_solicitados=indicadores.meses_solicitados,
            meses_com_dados=indicadores.meses_com_dados,
            valor_total=numero(indicadores.valor_total),
            beneficiarios_media_mensal=numero(indicadores.beneficiarios_media_mensal),
            valor_medio_por_beneficiario=numero(indicadores.valor_medio_por_beneficiario),
        )


class IndicadoresMunicipioResposta(BaseModel):
    fonte: Fonte
    municipio: MunicipioResposta
    periodo: PeriodoResposta
    indicadores: IndicadoresResposta
