from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep
from app.api.v1.parametros import Ano, CodigoIbge, MesFim, MesInicio

router = APIRouter(tags=["comparações"])


@router.get("/comparacoes/municipios", summary="Cards de duas cidades no mesmo período (RF02)")
def comparacao_municipios(
    request: Request,
    contrato: ContratoMockDep,
    codigo_ibge_a: CodigoIbge,
    codigo_ibge_b: CodigoIbge,
    ano: Ano,
    mes_inicio: MesInicio,
    mes_fim: MesFim = None,
) -> JSONResponse:
    return contrato.responder(request)
