# Comparativo do Novo Bolsa Família

Back-end em Python (FastAPI) e cliente em Vue.js, orquestrados com Docker Compose.

## Estrutura

```text
.
├── docker-compose.yml   # orquestra backend (e futuramente o frontend)
├── .env.example         # copie para .env
├── backend/             # API FastAPI
└── frontend/            # cliente Vue.js (etapa posterior)
```

## Executar

```bash
cp .env.example .env              # opcional com MODO_MOCK=true
docker compose up --build backend
```

- Health: http://localhost:8000/api/v1/health
- Swagger: http://localhost:8000/docs

Com `MODO_MOCK=true` (padrão) a API usa os dados fictícios de `backend/app/data/mock/` e não precisa de chave.
Para consultar o Portal da Transparência, preencha `PORTAL_TRANSPARENCIA_API_KEY` no `.env` e defina `MODO_MOCK=false`.

## Testes

```bash
docker compose --profile test run --rm --build backend-tests
```
