from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep
from app.api.v1.parametros import Ano, CodigoIbge, MesFim, MesInicio
from app.schemas.comparacao import MetricaRanking

router = APIRouter(tags=["comparações"])


@router.get("/capitais/comparacao", summary="Município de referência comparado às capitais, com ranking (RF04)")
def comparacao_capitais(
    request: Request,
    contrato: ContratoMockDep,
    codigo_ibge_referencia: CodigoIbge,
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
    capitais: Annotated[
        str | None,
        Query(description="UFs das capitais separadas por vírgula. Ausente: as 27", examples=["SC,PR,RS"]),
    ] = None,
    metrica: Annotated[MetricaRanking, Query(description="Métrica do ranking")] = MetricaRanking.valor_total,
) -> JSONResponse:
    return contrato.responder(request)
