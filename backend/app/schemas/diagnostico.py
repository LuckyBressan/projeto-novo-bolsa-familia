from datetime import datetime

from pydantic import BaseModel


class EstatisticasCache(BaseModel):
    itens: int
    hits: int
    misses: int
    ttl_segundos: int


class ConsumoResposta(BaseModel):
    modo_mock: bool
    limite_rpm_configurado: int
    chamadas_ultimo_minuto: int
    chamadas_desde_inicio: int
    chamadas_bloqueadas_pelo_limitador: int
    cache: EstatisticasCache
    iniciado_em: datetime
