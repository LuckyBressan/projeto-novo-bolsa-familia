from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep

router = APIRouter(tags=["diagnóstico"])


@router.get("/diagnostico/consumo", summary="Contadores de consumo da API do Portal e do cache (RNF01)")
def consumo(request: Request, contrato: ContratoMockDep) -> JSONResponse:
    return contrato.responder(request)
