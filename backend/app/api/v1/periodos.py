from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.contrato_mock import ContratoMockDep

router = APIRouter(tags=["catálogos"])


@router.get("/periodos", summary="Anos e meses válidos para os seletores")
def periodos(request: Request, contrato: ContratoMockDep) -> JSONResponse:
    return contrato.responder(request)
