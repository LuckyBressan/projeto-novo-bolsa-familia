import type { FiltroPeriodo } from './periodo'

export const SEM_VALOR = '—'

const NOMES_MES = [
  'jan',
  'fev',
  'mar',
  'abr',
  'mai',
  'jun',
  'jul',
  'ago',
  'set',
  'out',
  'nov',
  'dez',
]

export function nomearMes(mes: number): string {
  return NOMES_MES[mes - 1] ?? SEM_VALOR
}

export function formatarMes(mes: string): string {
  const [ano, numero] = mes.split('-')
  return `${nomearMes(Number(numero))}/${ano}`
}

export function formatarPeriodo(periodo: FiltroPeriodo): string {
  const inicio = `${nomearMes(periodo.mesInicio)}/${periodo.ano}`
  if (periodo.mesInicio === periodo.mesFim) return inicio
  return `${inicio} a ${nomearMes(periodo.mesFim)}/${periodo.ano}`
}

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

const moedaCompacta = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  maximumSignificantDigits: 3,
})

const inteiro = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 })

const inteiroCompacto = new Intl.NumberFormat('pt-BR', {
  notation: 'compact',
  maximumSignificantDigits: 3,
})

export function formatarInteiro(valor: number | null): string {
  return valor === null ? SEM_VALOR : inteiro.format(valor)
}

export function formatarInteiroCompacto(valor: number | null): string {
  return valor === null ? SEM_VALOR : inteiroCompacto.format(valor)
}

const hora = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' })

export function formatarHora(momento: number): string {
  return hora.format(momento)
}

export function formatarVariacao(valor: number | null): string {
  if (valor === null) return SEM_VALOR
  if (valor > 0) return `▲ +${inteiro.format(valor)}`
  if (valor < 0) return `▼ −${inteiro.format(-valor)}`
  return '= 0'
}

export function formatarMoeda(valor: number | null): string {
  return valor === null ? SEM_VALOR : moeda.format(valor)
}

export function formatarMoedaCompacta(valor: number | null): string {
  return valor === null ? SEM_VALOR : moedaCompacta.format(valor)
}

export function formatarPosicao(posicao: number | null): string {
  return posicao === null ? SEM_VALOR : `${posicao}º`
}
