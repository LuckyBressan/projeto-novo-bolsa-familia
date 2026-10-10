from fastapi import FastAPI

from app.api.v1 import capitais, comparacoes, diagnostico, estados, evolucao, health, municipios, periodos

app = FastAPI(title="Comparativo do Novo Bolsa Família", version="0.1.0")

for modulo in (health, periodos, estados, municipios, comparacoes, evolucao, capitais, diagnostico):
    app.include_router(modulo.router, prefix="/api/v1")
