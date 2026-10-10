import csv
import json
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from app.core.errors import EstadoInvalido, MunicipioInvalido


@dataclass(frozen=True)
class Estado:
    codigo_uf: str
    uf: str
    nome: str


@dataclass(frozen=True)
class Municipio:
    codigo_ibge: str
    nome: str
    uf: str


def chave_nome(nome: str) -> str:
    return unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().casefold()


class Catalogo:
    def __init__(self, estados: list[Estado], municipios: list[Municipio], capitais: list[Municipio]):
        self._estados = sorted(estados, key=lambda estado: chave_nome(estado.nome))
        self._municipios = sorted(municipios, key=lambda municipio: chave_nome(municipio.nome))
        self._municipios_codigo = {municipio.codigo_ibge: municipio for municipio in municipios}
        self._capitais = capitais

    def estados(self) -> list[Estado]:
        return list(self._estados)

    def validar_uf(self, uf: str) -> str:
        sigla = uf.upper()
        if all(estado.uf != sigla for estado in self._estados):
            raise EstadoInvalido(detalhes={"uf": uf})
        return sigla

    def municipios_uf(self, uf: str, busca: str | None = None) -> list[Municipio]:
        sigla = self.validar_uf(uf)
        trecho = chave_nome(busca or "")
        return [
            municipio
            for municipio in self._municipios
            if municipio.uf == sigla and trecho in chave_nome(municipio.nome)
        ]

    def capitais(self) -> list[Municipio]:
        return list(self._capitais)

    def municipio(self, codigo_ibge: str) -> Municipio:
        municipio = self._municipios_codigo.get(codigo_ibge)
        if municipio is None:
            raise MunicipioInvalido(detalhes={"codigo_ibge": codigo_ibge})
        return municipio


def _ler_json(caminho: Path) -> list[dict]:
    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_catalogo(pasta_dados: Path, modo_mock: bool, pasta_mock: Path | None = None) -> Catalogo:
    estados = [Estado(item["codigo_uf"], item["uf"], item["nome"]) for item in _ler_json(pasta_dados / "estados.json")]
    capitais = [Municipio(item["codigo_ibge"], item["nome"], item["uf"]) for item in _ler_json(pasta_dados / "capitais.json")]
    if modo_mock:
        linhas = _ler_json((pasta_mock or pasta_dados / "mock") / "catalogos" / "municipios-mock.json")
    else:
        with open(pasta_dados / "municipios.csv", encoding="utf-8", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo))
    municipios = [Municipio(linha["codigo_ibge"], linha["nome"], linha["uf"]) for linha in linhas]
    return Catalogo(estados=estados, municipios=municipios, capitais=capitais)
