from enum import StrEnum

from pydantic import BaseModel

from app.schemas.indicadores import Fonte, IndicadoresResposta
from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta


class MetricaRanking(StrEnum):
    valor_total = "valor_total"
    beneficiarios_media_mensal = "beneficiarios_media_mensal"
    valor_medio_por_beneficiario = "valor_medio_por_beneficiario"


class EntradaComparacao(BaseModel):
    municipio: MunicipioResposta
    indicadores: IndicadoresResposta


class ComparacaoResposta(BaseModel):
    fonte: Fonte
    periodo: PeriodoResposta
    municipios: list[EntradaComparacao]
