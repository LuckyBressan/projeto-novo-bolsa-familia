from fastapi import APIRouter

from app.api.dependencias import RegraPeriodoDep
from app.schemas.periodo import AnoMeses, PeriodosResposta

router = APIRouter(tags=["catálogos"])


@router.get("/periodos", response_model=PeriodosResposta, summary="Anos e meses válidos para os seletores")
def periodos(regra: RegraPeriodoDep) -> PeriodosResposta:
    return PeriodosResposta(
        periodo_min=regra.periodo_min,
        periodo_max=regra.periodo_max,
        max_meses_intervalo=regra.max_meses_intervalo,
        anos=[AnoMeses(ano=ano, meses=meses) for ano, meses in regra.anos_disponiveis().items()],
    )
