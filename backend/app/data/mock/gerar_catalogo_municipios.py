"""
Gera o catálogo completo de municípios (municipios.csv) a partir da API de localidades do IBGE.

Passo 1 — baixar o JSON do IBGE (no seu computador, com acesso à internet):
    PowerShell:
        Invoke-WebRequest "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado" -OutFile ibge_municipios.json
    ou bash:
        curl -o ibge_municipios.json "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?view=nivelado"

Passo 2 — converter:
    python -I gerar_catalogo_municipios.py ibge_municipios.json ../../backend/app/data/municipios.csv

Aceita o formato "nivelado" (?view=nivelado) e o formato aninhado padrão.
Saída: CSV UTF-8 com colunas codigo_ibge,nome,uf ordenado por UF e nome.
Registre a data do download no README do back-end (versão do catálogo).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def extrair(item: dict) -> tuple[str, str, str]:
    if "municipio-id" in item:  # view=nivelado
        return str(item["municipio-id"]), item["municipio-nome"], item["UF-sigla"]
    codigo, nome = str(item["id"]), item["nome"]
    micro = item.get("microrregiao") or {}
    uf = ((micro.get("mesorregiao") or {}).get("UF") or {}).get("sigla")
    if not uf:  # municípios recentes podem vir sem microrregião
        imediata = item.get("regiao-imediata") or {}
        uf = ((imediata.get("regiao-intermediaria") or {}).get("UF") or {}).get("sigla")
    if not uf:
        raise ValueError(f"UF não encontrada para o município {codigo} - {nome}")
    return codigo, nome, uf


def main(origem: str, destino: str) -> None:
    dados = json.loads(Path(origem).read_text(encoding="utf-8"))
    linhas = sorted({extrair(i) for i in dados}, key=lambda r: (r[2], r[1]))
    codigos = [l[0] for l in linhas]
    assert len(codigos) == len(set(codigos)), "códigos IBGE duplicados"
    assert all(len(c) == 7 and c.isdigit() for c in codigos), "código IBGE fora do padrão de 7 dígitos"
    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo_ibge", "nome", "uf"])
        w.writerows(linhas)
    print(f"{len(linhas)} municípios gravados em {destino}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("uso: python -I gerar_catalogo_municipios.py <ibge_municipios.json> <saida.csv>")
    main(sys.argv[1], sys.argv[2])
