import asyncio

from fastapi import APIRouter

from app.api.dependencias import CatalogoDep, FonteDadosDep, NomeFonteDep, RegraPeriodoDep
from app.api.v1.parametros import Ano, CodigoIbge, MesFim, MesInicio, garantir_cidades_diferentes
from app.schemas.evolucao import EvolucaoResposta, ItemSerieResposta, SerieMunicipio
from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.indicadores import calcular_serie, consultar_meses, falha_todos_meses

router = APIRouter(tags=["comparações"])


@router.get(
    "/evolucao-mensal",
    response_model=EvolucaoResposta,
    summary="Série mensal das duas cidades, com variação de beneficiários (RF03)",
)
async def evolucao_mensal(
    catalogo: CatalogoDep,
    regra: RegraPeriodoDep,
    fonte: FonteDadosDep,
    nome_fonte: NomeFonteDep,
    codigo_ibge_a: CodigoIbge,
    codigo_ibge_b: CodigoIbge,
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
) -> EvolucaoResposta:
    garantir_cidades_diferentes(codigo_ibge_a, codigo_ibge_b)
    periodo = regra.validar(ano, mes_inicio, mes_fim)
    municipios = [catalogo.municipio(codigo_ibge_a), catalogo.municipio(codigo_ibge_b)]
    resultados = await asyncio.gather(
        *(consultar_meses(fonte, municipio.codigo_ibge, periodo.meses) for municipio in municipios)
    )
    falha = falha_todos_meses(list(resultados))
    if falha is not None:
        raise falha
    return EvolucaoResposta(
        fonte=nome_fonte,
        periodo=PeriodoResposta.criar(periodo),
        series=[
            SerieMunicipio(
                municipio=MunicipioResposta.criar(municipio),
                meses=[ItemSerieResposta.criar(item) for item in calcular_serie(resultados_municipio)],
            )
            for municipio, resultados_municipio in zip(municipios, resultados)
        ],
    )
