from pydantic import BaseModel

from app.services.catalogos import Estado, Municipio


class EstadoResposta(BaseModel):
    codigo_uf: str
    uf: str
    nome: str


class ListaEstadosResposta(BaseModel):
    items: list[EstadoResposta]
    total: int

    @classmethod
    def criar(cls, estados: list[Estado]) -> "ListaEstadosResposta":
        return cls(
            items=[EstadoResposta(codigo_uf=estado.codigo_uf, uf=estado.uf, nome=estado.nome) for estado in estados],
            total=len(estados),
        )


class MunicipioResposta(BaseModel):
    codigo_ibge: str
    nome: str
    uf: str

    @classmethod
    def criar(cls, municipio: Municipio) -> "MunicipioResposta":
        return cls(codigo_ibge=municipio.codigo_ibge, nome=municipio.nome, uf=municipio.uf)


class ListaMunicipiosResposta(BaseModel):
    items: list[MunicipioResposta]
    total: int
