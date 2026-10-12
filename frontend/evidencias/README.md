# Evidências do front-end

Rodada de 12/10/2026, com o sistema no ar pelo Docker Compose (http://localhost:8080).

## Acessibilidade e temas (RNF03)

Com `MODO_MOCK=true`.

| Arquivo | O que mostra |
|---|---|
| `acessibilidade-axe.json` | Varredura do axe-core nas duas telas, com resultado na tela, nos três temas, em 1366 px e 390 px: nenhuma violação nas 12 combinações |
| `lighthouse.json` | Lighthouse (desktop): Acessibilidade 100 e Boas práticas 100 nas duas telas |
| `cidades-<tema>-<largura>.png` | Comparar cidades, Blumenau × Joinville, out–dez/2023 (cenário com mês sem dados) |
| `capitais-<tema>-<largura>.png` | Capitais, referência Rio do Sul, jan–mar/2024, todas as capitais |

Temas: `claro`, `escuro` e `contraste` (alto contraste). Larguras: `1366` (desktop) e `390` (celular).

## Homologação dos valores (Objetivo 5)

Com `MODO_MOCK=false`. Os números da tela são iguais aos de `backend/evidencias/amostra-homologacao.csv`.

| Arquivo | Caso da amostra | Valor total | Beneficiários | Valor médio |
|---|---|---|---|---|
| `homologacao-real-manaus-salvador-2024-01.png` | Manaus (AM), jan/2024 | R$ 185.493.269,00 | 269.720 | R$ 687,73 |
| `homologacao-real-manaus-salvador-2024-01.png` | Salvador (BA), jan/2024 | R$ 186.029.838,00 | 295.128 | R$ 630,34 |
| `homologacao-real-capitais-manaus-2023-03.png` | Manaus (AM), mar/2023, pela tela de capitais | R$ 163.325.605,00 | 250.324 | R$ 652,46 |

## Dados reais com nome longo e valores grandes

| Arquivo | O que mostra |
|---|---|
| `real-nome-longo-sp-rj-2026.png` | Referência São José do Vale do Rio Preto (RJ) com São Paulo e Rio de Janeiro, jun–ago/2026, em 1366 px |
| `real-nome-longo-celular.png` | O mesmo caso em 360 px, sem rolagem horizontal da página |
