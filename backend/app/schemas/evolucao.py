from pydantic import BaseModel

from app.schemas.indicadores import Fonte, StatusDado, numero
from app.schemas.municipio import MunicipioResposta
from app.schemas.periodo import PeriodoResposta
from app.services.indicadores import ItemSerie


class ItemSerieResposta(BaseModel):
    mes: str
    status_dado: StatusDado
    valor_total: float | None
    beneficiarios: int | None
    valor_medio_por_beneficiario: float | None
    variacao_beneficiarios_absoluta: int | None

    @classmethod
    def criar(cls, item: ItemSerie) -> "ItemSerieResposta":
        return cls(
            mes=item.mes,
            status_dado=item.status_dado,
            valor_total=numero(item.valor_total),
            beneficiarios=item.beneficiarios,
            valor_medio_por_beneficiario=numero(item.valor_medio_por_beneficiario),
            variacao_beneficiarios_absoluta=item.variacao_beneficiarios_absoluta,
        )


class SerieMunicipio(BaseModel):
    municipio: MunicipioResposta
    meses: list[ItemSerieResposta]


class EvolucaoResposta(BaseModel):
    fonte: Fonte
    periodo: PeriodoResposta
    series: list[SerieMunicipio]
