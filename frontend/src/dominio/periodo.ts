import type { Periodos } from '@/api/tipos'

export function listarAnos(periodos: Periodos): number[] {
  return periodos.anos.map((item) => item.ano)
}

export function listarMeses(periodos: Periodos, ano: number): number[] {
  return periodos.anos.find((item) => item.ano === ano)?.meses ?? []
}

export interface FiltroPeriodo {
  ano: number
  mesInicio: number
  mesFim: number
}

function limitar(valor: number, minimo: number, maximo: number): number {
  return Math.min(Math.max(valor, minimo), maximo)
}

export function ajustarPeriodo(periodos: Periodos, filtro: FiltroPeriodo): FiltroPeriodo {
  const meses = listarMeses(periodos, filtro.ano)
  const primeiro = meses[0]
  const ultimo = meses.at(-1)
  if (primeiro === undefined || ultimo === undefined) return filtro
  const mesInicio = limitar(filtro.mesInicio, primeiro, ultimo)
  const ultimoPermitido = Math.min(ultimo, mesInicio + periodos.max_meses_intervalo - 1)
  const mesFim = limitar(filtro.mesFim, mesInicio, ultimoPermitido)
  return { ano: filtro.ano, mesInicio, mesFim }
}

export function calcularPeriodoPadrao(periodos: Periodos): FiltroPeriodo | null {
  const recente = periodos.anos.at(-1)
  const mesFim = recente?.meses.at(-1)
  if (!recente || mesFim === undefined) return null
  const meses = recente.meses.slice(-periodos.max_meses_intervalo)
  return { ano: recente.ano, mesInicio: meses[0] ?? mesFim, mesFim }
}

export function validarPeriodo(periodos: Periodos, filtro: FiltroPeriodo): boolean {
  const meses = listarMeses(periodos, filtro.ano)
  return (
    meses.includes(filtro.mesInicio) &&
    meses.includes(filtro.mesFim) &&
    filtro.mesFim >= filtro.mesInicio &&
    filtro.mesFim - filtro.mesInicio < periodos.max_meses_intervalo
  )
}

function lerInteiro(valor: unknown): number | null {
  return typeof valor === 'string' && /^\d+$/.test(valor) ? Number(valor) : null
}

export function lerPeriodoQuery(
  periodos: Periodos,
  query: Record<string, unknown>,
): FiltroPeriodo | null {
  const ano = lerInteiro(query.ano)
  const mesInicio = lerInteiro(query.mesInicio)
  const mesFim = lerInteiro(query.mesFim)
  if (ano === null || mesInicio === null || mesFim === null) return null
  const filtro = { ano, mesInicio, mesFim }
  return validarPeriodo(periodos, filtro) ? filtro : null
}

export interface OpcaoMes {
  mes: number
  desabilitado: boolean
}

export function listarOpcoesMesFim(periodos: Periodos, ano: number, mesInicio: number): OpcaoMes[] {
  const ultimoPermitido = mesInicio + periodos.max_meses_intervalo - 1
  return listarMeses(periodos, ano).map((mes) => ({
    mes,
    desabilitado: mes < mesInicio || mes > ultimoPermitido,
  }))
}
