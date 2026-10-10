from pydantic import BaseModel

from app.schemas.comparacao import MetricaRanking
from app.schemas.evolucao import ItemSerieResposta
from app.schemas.indicadores import Fonte, IndicadoresResposta
from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.capitais import EntradaRanking


class CapitalResposta(BaseModel):
    municipio: MunicipioResposta
    indicadores: IndicadoresResposta
    meses: list[ItemSerieResposta]
    posicao_ranking: int | None

    @classmethod
    def criar(cls, entrada: EntradaRanking) -> "CapitalResposta":
        return cls(
            municipio=MunicipioResposta.criar(entrada.municipio),
            indicadores=IndicadoresResposta.criar(entrada.indicadores),
            meses=[ItemSerieResposta.criar(item) for item in entrada.serie],
            posicao_ranking=entrada.posicao_ranking,
        )


class ReferenciaResposta(BaseModel):
    municipio: MunicipioResposta
    indicadores: IndicadoresResposta
    meses: list[ItemSerieResposta]
    posicao_entre_capitais: int | None


class ComparacaoCapitaisResposta(BaseModel):
    fonte: Fonte
    periodo: PeriodoResposta
    metrica_ranking: MetricaRanking
    filtro_capitais: list[str] | None
    total_capitais: int
    referencia: ReferenciaResposta
    capitais: list[CapitalResposta]
