from pydantic import BaseModel


class HealthResposta(BaseModel):
    status: str
    service: str
    modo_mock: bool
