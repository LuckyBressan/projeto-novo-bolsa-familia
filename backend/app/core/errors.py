import logging
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErroApi(Exception):
    codigo = "ERRO_INTERNO"
    http_status = 500
    mensagem = "Ocorreu um erro inesperado."

    def __init__(self, mensagem: str | None = None, detalhes: dict[str, Any] | None = None):
        self.mensagem = mensagem or self.mensagem
        self.detalhes = detalhes or {}
        super().__init__(self.mensagem)


class ParametroInvalido(ErroApi):
    codigo = "PARAMETRO_INVALIDO"
    http_status = 422
    mensagem = "Parâmetro ausente ou com formato inválido."


class PeriodoInvalido(ErroApi):
    codigo = "PERIODO_INVALIDO"
    http_status = 422
    mensagem = "Período inválido."


class EstadoInvalido(ErroApi):
    codigo = "ESTADO_INVALIDO"
    http_status = 422
    mensagem = "UF inexistente."


class MunicipioInvalido(ErroApi):
    codigo = "MUNICIPIO_INVALIDO"
    http_status = 404
    mensagem = "Município não encontrado no catálogo."


class ErroFonte(ErroApi):
    """Falha ao obter dados do Portal; nas rotas com várias entradas vira fonte_indisponivel."""


class FonteIndisponivel(ErroFonte):
    codigo = "FONTE_INDISPONIVEL"
    http_status = 503
    mensagem = "Não foi possível consultar os dados oficiais neste momento."


class RespostaFonteInvalida(ErroFonte):
    codigo = "RESPOSTA_FONTE_INVALIDA"
    http_status = 502
    mensagem = "O Portal da Transparência respondeu em um formato inesperado."


class LimiteFonteExcedido(ErroFonte):
    codigo = "LIMITE_FONTE_EXCEDIDO"
    http_status = 503
    mensagem = "O Portal da Transparência recusou a consulta por excesso de requisições. Tente novamente em instantes."


def resposta_erro(erro: ErroApi) -> JSONResponse:
    correlacao_id = uuid.uuid4().hex
    logger.warning("Erro %s (%s) correlacao_id=%s", erro.codigo, erro.mensagem, correlacao_id)
    corpo: dict[str, Any] = {"codigo": erro.codigo, "mensagem": erro.mensagem}
    if erro.detalhes:
        corpo["detalhes"] = erro.detalhes
    corpo["correlacao_id"] = correlacao_id
    return JSONResponse({"erro": corpo}, status_code=erro.http_status)


def registrar_tratadores(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(request: Request, erro: RequestValidationError) -> JSONResponse:
        campos = list(dict.fromkeys(str(item["loc"][-1]) for item in erro.errors()))
        return resposta_erro(ParametroInvalido(detalhes={"campos": campos}))

    @app.exception_handler(ErroApi)
    async def tratar_erro_api(request: Request, erro: ErroApi) -> JSONResponse:
        return resposta_erro(erro)

    @app.exception_handler(Exception)
    async def tratar_erro_inesperado(request: Request, erro: Exception) -> JSONResponse:
        logger.exception("Erro inesperado em %s %s", request.method, request.url.path)
        return resposta_erro(ErroApi())
