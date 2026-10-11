import type { FiltrosCapitais, FiltrosComparacao } from '@/dominio/filtros'
import type { FiltroPeriodo } from '@/dominio/periodo'
import { obter } from './cliente'
import type {
  Comparacao,
  ComparacaoCapitais,
  Evolucao,
  ListaEstados,
  ListaMunicipios,
  Periodos,
  Saude,
} from './tipos'

type Parametros = Record<string, string>

export interface DefinicaoConsulta<Filtros, Resposta> {
  rota: string
  montarParametros(filtros: Filtros): Parametros
  buscar(parametros: Parametros, controle: AbortController): Promise<Resposta>
}

export const TEMPOS_LIMITE_MS = {
  catalogo: 10_000,
  comparacao: 75_000,
  capitais: 90_000,
} as const

function definir<Filtros, Resposta>(
  rota: string,
  tempoLimiteMs: number,
  montarParametros: (filtros: Filtros) => Parametros,
): DefinicaoConsulta<Filtros, Resposta> {
  return {
    rota,
    montarParametros,
    buscar: (parametros, controle) =>
      obter<Resposta>(rota, parametros, { controle, tempoLimiteMs }),
  }
}

function obterCatalogo<Resposta>(caminho: string, parametros: Parametros = {}): Promise<Resposta> {
  return obter<Resposta>(caminho, parametros, {
    controle: new AbortController(),
    tempoLimiteMs: TEMPOS_LIMITE_MS.catalogo,
  })
}

export function buscarSaude(): Promise<Saude> {
  return obterCatalogo('/health')
}

export function buscarPeriodos(): Promise<Periodos> {
  return obterCatalogo('/periodos')
}

export function buscarEstados(): Promise<ListaEstados> {
  return obterCatalogo('/estados')
}

export function buscarMunicipiosByUf(uf: string): Promise<ListaMunicipios> {
  return obterCatalogo('/municipios', { uf })
}

function montarPeriodo(filtros: FiltroPeriodo): Parametros {
  return {
    ano: String(filtros.ano),
    mes_inicio: String(filtros.mesInicio),
    mes_fim: String(filtros.mesFim),
  }
}

function montarCidades(filtros: FiltrosComparacao): Parametros {
  return {
    codigo_ibge_a: filtros.cidadeA,
    codigo_ibge_b: filtros.cidadeB,
    ...montarPeriodo(filtros),
  }
}

export const consultaComparacao = definir<FiltrosComparacao, Comparacao>(
  '/comparacoes/municipios',
  TEMPOS_LIMITE_MS.comparacao,
  montarCidades,
)

export const consultaEvolucao = definir<FiltrosComparacao, Evolucao>(
  '/evolucao-mensal',
  TEMPOS_LIMITE_MS.comparacao,
  montarCidades,
)

function montarCapitais(filtros: FiltrosCapitais): Parametros {
  const parametros: Parametros = {
    codigo_ibge_referencia: filtros.referencia,
    ...montarPeriodo(filtros),
    metrica: filtros.metrica,
  }
  if (filtros.capitais?.length) parametros.capitais = filtros.capitais.join(',')
  return parametros
}

export const consultaCapitais = definir<FiltrosCapitais, ComparacaoCapitais>(
  '/capitais/comparacao',
  TEMPOS_LIMITE_MS.capitais,
  montarCapitais,
)
