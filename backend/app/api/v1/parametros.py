from typing import Annotated

from fastapi import Query

CodigoIbge = Annotated[str, Query(description="Código IBGE do município, 7 dígitos", examples=["4214805"])]
Ano = Annotated[int, Query(description="Ano do período", examples=[2024])]
MesInicio = Annotated[int, Query(ge=1, le=12, description="Primeiro mês do período (1 a 12)", examples=[1])]
MesFim = Annotated[
    int | None,
    Query(ge=1, le=12, description="Último mês do período (1 a 12). Padrão: mes_inicio. No máximo 3 meses", examples=[3]),
]
