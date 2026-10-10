import asyncio

from fastapi import APIRouter

from app.api.dependencias import CatalogoDep, FonteDadosDep, NomeFonteDep, RegraPeriodoDep
from app.api.v1.parametros import Ano, CodigoIbge, MesFim, MesInicio
from app.core.errors import ParametroInvalido
from app.schemas.comparacao import ComparacaoResposta, EntradaComparacao
from app.schemas.indicadores import IndicadoresResposta
from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.indicadores import calcular_indicadores, consultar_meses, falha_todas_entradas

router = APIRouter(tags=["comparações"])


@router.get(
    "/comparacoes/municipios",
    response_model=ComparacaoResposta,
    summary="Cards de duas cidades no mesmo período (RF02)",
)
async def comparacao_municipios(
    catalogo: CatalogoDep,
    regra: RegraPeriodoDep,
    fonte: FonteDadosDep,
    nome_fonte: NomeFonteDep,
    codigo_ibge_a: CodigoIbge,
    codigo_ibge_b: CodigoIbge,
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
) -> ComparacaoResposta:
    if codigo_ibge_a == codigo_ibge_b:
        raise ParametroInvalido(
            "As duas cidades devem ser diferentes.",
            {"campos": ["codigo_ibge_a", "codigo_ibge_b"]},
        )
    periodo = regra.validar(ano, mes_inicio, mes_fim)
    municipios = [catalogo.municipio(codigo_ibge_a), catalogo.municipio(codigo_ibge_b)]
    resultados = await asyncio.gather(
        *(consultar_meses(fonte, municipio.codigo_ibge, periodo.meses) for municipio in municipios)
    )
    falha = falha_todas_entradas(list(resultados))
    if falha is not None:
        raise falha
    return ComparacaoResposta(
        fonte=nome_fonte,
        periodo=PeriodoResposta.criar(periodo),
        municipios=[
            EntradaComparacao(
                municipio=MunicipioResposta.criar(municipio),
                indicadores=IndicadoresResposta.criar(calcular_indicadores(resultados_municipio)),
            )
            for municipio, resultados_municipio in zip(municipios, resultados)
        ],
    )
