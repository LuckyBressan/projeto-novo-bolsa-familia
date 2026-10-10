from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep
from app.api.v1.parametros import Ano, MesFim, MesInicio

router = APIRouter(tags=["municípios"])


@router.get("/municipios", summary="Municípios de uma UF, com busca opcional pelo nome")
def municipios(
    request: Request,
    contrato: ContratoMockDep,
    uf: Annotated[str, Query(description="Sigla da UF", examples=["SC"])],
    busca: Annotated[str | None, Query(description="Parte do nome, sem diferenciar maiúsculas e acentos")] = None,
) -> JSONResponse:
    return contrato.responder(request)


@router.get("/municipios/{codigo_ibge}/indicadores", summary="Cards de um município no período")
def indicadores(
    request: Request,
    contrato: ContratoMockDep,
    codigo_ibge: Annotated[str, Path(description="Código IBGE do município, 7 dígitos", examples=["4214805"])],
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
) -> JSONResponse:
    return contrato.responder(request)
