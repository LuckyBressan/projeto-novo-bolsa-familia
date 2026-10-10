from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep
from app.api.v1.parametros import Ano, CodigoIbge, MesFim, MesInicio

router = APIRouter(tags=["comparações"])


@router.get("/evolucao-mensal", summary="Série mensal das duas cidades, com variação de beneficiários (RF03)")
def evolucao_mensal(
    request: Request,
    contrato: ContratoMockDep,
    codigo_ibge_a: CodigoIbge,
    codigo_ibge_b: CodigoIbge,
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
) -> JSONResponse:
    return contrato.responder(request)
