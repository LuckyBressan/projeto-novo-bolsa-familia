from fastapi import APIRouter

from app.api.dependencias import CatalogoDep
from app.schemas.municipio import ListaEstadosResposta

router = APIRouter(tags=["catálogos"])


@router.get("/estados", response_model=ListaEstadosResposta, summary="As 27 UFs, ordenadas por nome")
def estados(catalogo: CatalogoDep) -> ListaEstadosResposta:
    return ListaEstadosResposta.criar(catalogo.estados())
