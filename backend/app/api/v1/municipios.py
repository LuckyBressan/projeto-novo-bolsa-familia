from typing import Annotated

from fastapi import APIRouter, Path, Query

from app.api.dependencias import CatalogoDep, FonteDadosDep, NomeFonteDep, RegraPeriodoDep
from app.api.v1.parametros import Ano, MesFim, MesInicio
from app.schemas.indicadores import IndicadoresMunicipioResposta, IndicadoresResposta
from app.schemas.municipio import ListaMunicipiosResposta, MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.indicadores import calcular_indicadores, consultar_meses, primeira_falha

router = APIRouter(tags=["municípios"])


@router.get(
    "/municipios",
    response_model=ListaMunicipiosResposta,
    summary="Municípios de uma UF, com busca opcional pelo nome",
)
def municipios(
    catalogo: CatalogoDep,
    uf: Annotated[str, Query(description="Sigla da UF", examples=["SC"])],
    busca: Annotated[str | None, Query(description="Parte do nome, sem diferenciar maiúsculas e acentos")] = None,
) -> ListaMunicipiosResposta:
    encontrados = catalogo.municipios_uf(uf, busca)
    return ListaMunicipiosResposta(items=[MunicipioResposta.criar(item) for item in encontrados], total=len(encontrados))


@router.get(
    "/municipios/{codigo_ibge}/indicadores",
    response_model=IndicadoresMunicipioResposta,
    summary="Cards de um município no período",
)
async def indicadores(
    catalogo: CatalogoDep,
    regra: RegraPeriodoDep,
    fonte: FonteDadosDep,
    nome_fonte: NomeFonteDep,
    codigo_ibge: Annotated[str, Path(description="Código IBGE do município, 7 dígitos", examples=["4214805"])],
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
) -> IndicadoresMunicipioResposta:
    periodo = regra.validar(ano, mes_inicio, mes_fim)
    municipio = catalogo.municipio(codigo_ibge)
    resultados = await consultar_meses(fonte, municipio.codigo_ibge, periodo.meses)
    falha = primeira_falha(resultados)
    if falha is not None:
        raise falha
    return IndicadoresMunicipioResposta(
        fonte=nome_fonte,
        municipio=MunicipioResposta.criar(municipio),
        periodo=PeriodoResposta.criar(periodo),
        indicadores=IndicadoresResposta.criar(calcular_indicadores(resultados)),
    )
