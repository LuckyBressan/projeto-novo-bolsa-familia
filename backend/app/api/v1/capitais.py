from typing import Annotated

from fastapi import APIRouter, Query

from app.api.dependencias import CatalogoDep, FonteDadosDep, NomeFonteDep, RegraPeriodoDep
from app.api.v1.parametros import Ano, CodigoIbge, MesFim, MesInicio
from app.core.errors import MetricaInvalida
from app.schemas.capitais import CapitalResposta, ComparacaoCapitaisResposta, ReferenciaResposta
from app.schemas.comparacao import MetricaRanking
from app.schemas.evolucao import ItemSerieResposta
from app.schemas.indicadores import IndicadoresResposta
from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.capitais import comparar_capitais

router = APIRouter(tags=["comparações"])


@router.get(
    "/capitais/comparacao",
    response_model=ComparacaoCapitaisResposta,
    summary="Município de referência comparado às capitais, com ranking (RF04)",
)
async def comparacao_capitais(
    catalogo: CatalogoDep,
    regra: RegraPeriodoDep,
    fonte: FonteDadosDep,
    nome_fonte: NomeFonteDep,
    codigo_ibge_referencia: CodigoIbge,
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
    capitais: Annotated[
        str | None,
        Query(description="UFs das capitais separadas por vírgula. Ausente: as 27", examples=["SC,PR,RS"]),
    ] = None,
    metrica: Annotated[
        str,
        Query(description="Métrica do ranking", json_schema_extra={"enum": [item.value for item in MetricaRanking]}),
    ] = MetricaRanking.valor_total.value,
) -> ComparacaoCapitaisResposta:
    if metrica not in MetricaRanking:
        raise MetricaInvalida(
            detalhes={"metrica": metrica, "metricas_aceitas": [item.value for item in MetricaRanking]}
        )
    periodo = regra.validar(ano, mes_inicio, mes_fim)
    referencia = catalogo.municipio(codigo_ibge_referencia)
    capitais_filtradas, filtro = catalogo.capitais_ufs(capitais)
    comparacao = await comparar_capitais(fonte, referencia, capitais_filtradas, periodo.meses, metrica)
    return ComparacaoCapitaisResposta(
        fonte=nome_fonte,
        periodo=PeriodoResposta.criar(periodo),
        metrica_ranking=MetricaRanking(metrica),
        filtro_capitais=filtro,
        total_capitais=len(comparacao.capitais),
        referencia=ReferenciaResposta(
            municipio=MunicipioResposta.criar(comparacao.referencia.municipio),
            indicadores=IndicadoresResposta.criar(comparacao.referencia.indicadores),
            meses=[ItemSerieResposta.criar(item) for item in comparacao.referencia.serie],
            posicao_entre_capitais=comparacao.posicao_referencia,
        ),
        capitais=[CapitalResposta.criar(entrada) for entrada in comparacao.capitais],
    )
