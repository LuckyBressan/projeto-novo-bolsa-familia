from fastapi import APIRouter

from app.api.dependencias import FonteDadosDep, SettingsDep
from app.schemas.diagnostico import ConsumoResposta, EstatisticasCache

router = APIRouter(tags=["diagnóstico"])


@router.get(
    "/diagnostico/consumo",
    response_model=ConsumoResposta,
    summary="Contadores de consumo da API do Portal e do cache (RNF01)",
)
def consumo(fonte: FonteDadosDep, settings: SettingsDep) -> ConsumoResposta:
    return ConsumoResposta(
        modo_mock=settings.modo_mock,
        limite_rpm_configurado=fonte.limitador.limite_por_minuto,
        chamadas_ultimo_minuto=fonte.limitador.chamadas_ultimo_minuto(),
        chamadas_desde_inicio=fonte.limitador.chamadas_desde_inicio,
        chamadas_bloqueadas_pelo_limitador=fonte.limitador.chamadas_bloqueadas,
        cache=EstatisticasCache(
            itens=fonte.cache.itens,
            hits=fonte.cache.hits,
            misses=fonte.cache.misses,
            ttl_segundos=int(fonte.cache.ttl_segundos),
        ),
        iniciado_em=fonte.iniciado_em,
    )
