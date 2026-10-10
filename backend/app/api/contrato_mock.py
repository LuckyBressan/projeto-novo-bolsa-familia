import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import parse_qsl, urlsplit

from fastapi import Depends, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings


@dataclass(frozen=True)
class Exemplo:
    caminho: str
    parametros: dict[str, str]
    http_status: int
    corpo: Any


class ContratoMock:
    """Respostas estáticas de mock/api-v1, provisórias até a lógica real de cada rota existir."""

    def __init__(self, pasta: Path):
        pasta_exemplos = pasta / "api-v1"
        indice = json.loads((pasta_exemplos / "_rotas.json").read_text(encoding="utf-8"))
        self._exemplos = [self._carregar(pasta_exemplos, item) for item in indice]

    @staticmethod
    def _carregar(pasta_exemplos: Path, item: dict) -> Exemplo:
        url = urlsplit(item["rota"])
        return Exemplo(
            caminho=url.path,
            parametros=dict(parse_qsl(url.query)),
            http_status=item["http_status"],
            corpo=json.loads((pasta_exemplos / item["arquivo"]).read_text(encoding="utf-8")),
        )

    def responder(self, request: Request) -> JSONResponse:
        caminho = request.url.path
        parametros = dict(request.query_params)
        modelo = request.scope["route"].path
        exemplos_rota = [item for item in self._exemplos if _mesma_rota(item.caminho, caminho, modelo)]
        exemplo = next(
            (item for item in exemplos_rota if item.caminho == caminho and item.parametros == parametros),
            None,
        )
        if exemplo is None:
            exemplo = max(
                (item for item in exemplos_rota if item.http_status == 200),
                key=lambda item: _semelhanca(item, caminho, parametros),
            )
        return JSONResponse(exemplo.corpo, status_code=exemplo.http_status)


def _mesma_rota(caminho_exemplo: str, caminho: str, modelo: str) -> bool:
    partes_exemplo = caminho_exemplo.strip("/").split("/")
    partes = caminho.strip("/").split("/")
    # A rota no scope vem sem o prefixo do include_router, então o modelo é alinhado pelo fim do caminho.
    variaveis = [parte.startswith("{") for parte in modelo.strip("/").split("/")]
    variaveis = [False] * (len(partes) - len(variaveis)) + variaveis
    return len(partes_exemplo) == len(partes) and all(
        variavel or parte_exemplo == parte
        for parte_exemplo, parte, variavel in zip(partes_exemplo, partes, variaveis)
    )


def _semelhanca(exemplo: Exemplo, caminho: str, parametros: dict[str, str]) -> int:
    parametros_iguais = sum(1 for nome, valor in parametros.items() if exemplo.parametros.get(nome) == valor)
    return parametros_iguais + (exemplo.caminho == caminho)


@lru_cache
def get_contrato_mock() -> ContratoMock:
    return ContratoMock(get_settings().mock_dir)


ContratoMockDep = Annotated[ContratoMock, Depends(get_contrato_mock)]
