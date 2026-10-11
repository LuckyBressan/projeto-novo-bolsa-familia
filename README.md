# Comparativo do Novo Bolsa Família

Back-end em Python (FastAPI) e cliente em Vue.js, orquestrados com Docker Compose.

## Estrutura

```text
.
├── docker-compose.yml   # orquestra backend e frontend
├── .env.example         # copie para .env
├── backend/             # API FastAPI
└── frontend/            # cliente Vue 3 (Vite, TypeScript), servido por nginx
```

## Executar

### Docker completo (testes, homologação e apresentação)

```bash
cp .env.example .env              # opcional com MODO_MOCK=true
docker compose up --build
```

- Sistema: http://localhost:8080
- Health: http://localhost:8000/api/v1/health
- Swagger: http://localhost:8000/docs

O nginx do front-end serve a página e encaminha `/api` para o back-end, então o navegador só fala com a porta 8080. Para trocar as portas, use `FRONTEND_PORT` e `BACKEND_PORT` no `.env`.

### Desenvolvimento (recarga instantânea)

```bash
docker compose up --build backend   # API em http://localhost:8000
cd frontend
npm install
npm run dev                         # http://localhost:5173
```

O Vite encaminha `/api` para `http://localhost:8000`. Requer Node 24 (ou 22.18+).

Para apontar o front de desenvolvimento para outro back-end (por exemplo, um segundo contêiner em modo mock), use a variável `API_ALVO`:

```bash
docker run --rm -d -p 8001:8000 -e MODO_MOCK=true comparativo-bolsa-familia-backend
API_ALVO=http://localhost:8001 npm run dev
```

Com `MODO_MOCK=true` (padrão) a API usa os dados fictícios de `backend/app/data/mock/` e não precisa de chave.
Para consultar o Portal da Transparência, preencha `PORTAL_TRANSPARENCIA_API_KEY` no `.env` e defina `MODO_MOCK=false`.

## Catálogos

- `backend/app/data/estados.json` e `capitais.json`: 27 UFs e 27 capitais.
- `backend/app/data/municipios.csv`: 5.571 municípios, gerado com `backend/app/data/mock/gerar_catalogo_municipios.py` a partir da [API de localidades do IBGE](https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado), baixada em **09/10/2026**.
- Com `MODO_MOCK=true`, a lista de municípios usa só os 32 do mock (`backend/app/data/mock/catalogos/municipios-mock.json`).

## Testes

```bash
docker compose --profile test run --rm --build backend-tests
docker compose --profile test run --rm frontend-tests
```

O `frontend-tests` roda a checagem de tipos e os testes unitários (Vitest) num contêiner Node. Ele monta a raiz do repositório, porque os testes leem as respostas de `backend/app/data/mock/api-v1/`: o front é testado contra o mesmo contrato que o back-end garante.

Sem Docker, dentro de `frontend/`:

```bash
npm run test:unit -- --run
npm run type-check
npm run lint
```

Se o contrato da API mudar, gere os tipos de novo com o back-end no ar: `npm run gerar:tipos`.

## Simulação de carga (RNF01)

Com o back-end no ar, dispara consultas variadas em paralelo e confere o consumo em `/diagnostico/consumo`:

```bash
docker compose --profile test run --rm backend-tests \
  python scripts/simular_carga.py --base-url http://backend:8000 --saida evidencias/simulacao-carga-mock.json
```

- Aprovado quando o pico de chamadas por minuto não passa de `PORTAL_LIMITE_RPM` e nenhum erro de limite chega ao usuário.
- As 30 consultas padrão geram mais de 150 chamadas, então algumas respostas esperam cerca de 1 minuto: é o limitador segurando a fila.
- `--consultas`, `--paralelas` e `--semente` mudam o volume; a mesma semente repete as mesmas consultas.
- Rode com `MODO_MOCK=true`. No modo real, só uma rodada curta (`--consultas 20`), porque cada chamada gasta cota da chave.

## Amostra de homologação (Objetivo 5)

Com `MODO_MOCK=false`, consulta cada caso de `backend/scripts/amostra_homologacao.csv` direto no Portal e na API interna, mês a mês, e grava a planilha com os dois valores lado a lado:

```bash
MODO_MOCK=false docker compose up -d backend
docker compose --profile test run --rm --env-from-file .env backend-tests \
  python scripts/conferir_amostra.py --base-url http://backend:8000
```

- Saída em `backend/evidencias/amostra-homologacao.csv` (separador `;`, abre no Excel). A coluna `resultado` traz `ok`, `divergente` ou `nao_conferido` (uma das fontes falhou).
- Para mudar a amostra, edite as linhas `codigo_ibge;municipio;uf;mes` do arquivo de casos.
- Com `MODO_MOCK=true` o script recusa a execução: números do mock não valem como evidência.

As evidências das rodadas ficam em `backend/evidencias/`.
