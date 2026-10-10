import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import capitais, comparacoes, diagnostico, estados, evolucao, health, municipios, periodos
from app.core.config import get_settings
from app.core.errors import registrar_tratadores
from app.services.montagem import montar_fonte_dados


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper(), format="%(levelname)s:     %(name)s - %(message)s")
    logging.getLogger("app").info("Iniciando com MODO_MOCK=%s", settings.modo_mock)
    async with montar_fonte_dados(settings) as fonte_dados:
        app.state.fonte_dados = fonte_dados
        yield


app = FastAPI(title="Comparativo do Novo Bolsa Família", version="0.1.0", lifespan=ciclo_vida)
registrar_tratadores(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().lista_cors_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)

for modulo in (health, periodos, estados, municipios, comparacoes, evolucao, capitais, diagnostico):
    app.include_router(modulo.router, prefix="/api/v1")
