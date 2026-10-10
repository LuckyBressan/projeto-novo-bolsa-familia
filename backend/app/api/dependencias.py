from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.services.catalogos import Catalogo
from app.services.fonte_dados import FonteDados
from app.services.periodo import RegraPeriodo


def get_fonte_dados(request: Request) -> FonteDados:
    return request.app.state.fonte_dados


def get_catalogo(request: Request) -> Catalogo:
    return request.app.state.catalogo


def get_regra_periodo(settings: Annotated[Settings, Depends(get_settings)]) -> RegraPeriodo:
    return RegraPeriodo(settings.periodo_min, settings.periodo_max, settings.max_meses_intervalo)


def get_nome_fonte(settings: Annotated[Settings, Depends(get_settings)]) -> str:
    return "mock" if settings.modo_mock else "portal_transparencia"


FonteDadosDep = Annotated[FonteDados, Depends(get_fonte_dados)]
NomeFonteDep = Annotated[str, Depends(get_nome_fonte)]
CatalogoDep = Annotated[Catalogo, Depends(get_catalogo)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
RegraPeriodoDep = Annotated[RegraPeriodo, Depends(get_regra_periodo)]
