from typing import Annotated

from fastapi import Depends, Request

from app.core.config import Settings, get_settings
from app.services.fonte_dados import FonteDados


def get_fonte_dados(request: Request) -> FonteDados:
    return request.app.state.fonte_dados


FonteDadosDep = Annotated[FonteDados, Depends(get_fonte_dados)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
