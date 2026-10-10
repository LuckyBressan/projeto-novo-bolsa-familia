import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import FonteIndisponivel, registrar_tratadores
from app.main import app


def criar_app_erro(erro: Exception) -> FastAPI:
    app_erro = FastAPI()
    registrar_tratadores(app_erro)

    @app_erro.get("/falha")
    def falha():
        raise erro

    return app_erro


@pytest.mark.parametrize(
    ("rota", "campos"),
    [
        ("/api/v1/municipios/4214805/indicadores?ano=abc&mes_inicio=1", ["ano"]),
        ("/api/v1/municipios", ["uf"]),
    ],
)
def test_parametro_invalido_responde_envelope_contrato(rota, campos):
    with TestClient(app) as cliente:
        resposta = cliente.get(rota)

    assert resposta.status_code == 422
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "PARAMETRO_INVALIDO"
    assert erro["detalhes"] == {"campos": campos}
    assert erro["mensagem"]
    assert erro["correlacao_id"]


def test_erro_aplicacao_responde_envelope_com_status_do_erro():
    resposta = TestClient(criar_app_erro(FonteIndisponivel())).get("/falha")

    assert resposta.status_code == 503
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "FONTE_INDISPONIVEL"
    assert erro["mensagem"] == "Não foi possível consultar os dados oficiais neste momento."
    assert "detalhes" not in erro
    assert erro["correlacao_id"]


def test_erro_inesperado_responde_erro_interno_sem_expor_detalhes():
    app_erro = criar_app_erro(RuntimeError("detalhe interno chave-api-dados=abc"))

    resposta = TestClient(app_erro, raise_server_exceptions=False).get("/falha")

    assert resposta.status_code == 500
    assert resposta.json()["erro"]["codigo"] == "ERRO_INTERNO"
    assert "detalhe interno" not in resposta.text
    assert "Traceback" not in resposta.text
