from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep

router = APIRouter(tags=["catálogos"])


@router.get("/estados", summary="As 27 UFs, ordenadas por nome")
def estados(request: Request, contrato: ContratoMockDep) -> JSONResponse:
    return contrato.responder(request)
