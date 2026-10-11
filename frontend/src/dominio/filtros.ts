import type { Estado, MetricaRanking, Periodos } from '@/api/tipos'
import { calcularPeriodoPadrao, lerPeriodoQuery, type FiltroPeriodo } from './periodo'

export interface FiltrosComparacao extends FiltroPeriodo {
  cidadeA: string
  cidadeB: string
}

export interface FiltrosCapitais extends FiltroPeriodo {
  referencia: string
  capitais: string[] | null
  metrica: MetricaRanking
}

export interface EdicaoComparacao extends FiltroPeriodo {
  cidadeA: string | null
  cidadeB: string | null
}

type Query = Record<string, unknown>

function lerCodigoIbge(valor: unknown): string | null {
  return typeof valor === 'string' && /^\d{7}$/.test(valor) ? valor : null
}

function resolverPeriodo(periodos: Periodos, query: Query): FiltroPeriodo {
  const lido = lerPeriodoQuery(periodos, query) ?? calcularPeriodoPadrao(periodos)
  if (lido) return lido
  const [ano = 0, mes = 1] = periodos.periodo_max.split('-').map(Number)
  return { ano, mesInicio: mes, mesFim: mes }
}

const CHAVES_COMPARACAO = ['cidadeA', 'cidadeB', 'ano', 'mesInicio', 'mesFim']

function converterTexto(valores: object): Record<string, string> {
  return Object.fromEntries(
    Object.entries(valores)
      .filter(([, valor]) => valor !== null)
      .map(([nome, valor]) => [nome, String(valor)]),
  )
}

export function resolverFiltrosComparacao(
  periodos: Periodos,
  query: Query,
  guardados: EdicaoComparacao | null,
): EdicaoComparacao {
  const naUrl = CHAVES_COMPARACAO.some((chave) => chave in query)
  const origem = naUrl || !guardados ? query : converterTexto(guardados)
  const cidadeA = lerCodigoIbge(origem.cidadeA)
  const cidadeB = lerCodigoIbge(origem.cidadeB)
  return {
    cidadeA,
    cidadeB: cidadeB === cidadeA ? null : cidadeB,
    ...resolverPeriodo(periodos, origem),
  }
}

export function descreverPendenciaComparacao(filtros: EdicaoComparacao): string | null {
  if (!filtros.cidadeA) return 'Escolha a cidade A'
  if (!filtros.cidadeB) return 'Escolha a cidade B'
  return null
}

export function completarFiltrosComparacao(filtros: EdicaoComparacao): FiltrosComparacao | null {
  const { cidadeA, cidadeB } = filtros
  return cidadeA && cidadeB ? { ...filtros, cidadeA, cidadeB } : null
}

export function montarQueryComparacao(filtros: EdicaoComparacao): Record<string, string> {
  return converterTexto(filtros)
}

export function encontrarUf(estados: Estado[], codigoIbge: string | null): string | null {
  if (!codigoIbge) return null
  const codigoUf = codigoIbge.slice(0, 2)
  return estados.find((estado) => estado.codigo_uf === codigoUf)?.uf ?? null
}
