import type { Modo } from '@/api/tipos'

export const VALIDADE_RESULTADO_MS = 60 * 60 * 1000

export function conferirValidade(salvoEm: number, agora: number, validadeMs: number): boolean {
  const idade = agora - salvoEm
  return idade >= 0 && idade < validadeMs
}

export const LIMITE_RESULTADOS = 20

export interface EntradaCache<Dados = unknown> {
  chave: string
  salvoEm: number
  dados: Dados
}

export function adicionarEntrada(
  entradas: EntradaCache[],
  nova: EntradaCache,
  limite: number = LIMITE_RESULTADOS,
): EntradaCache[] {
  return [...entradas.filter((entrada) => entrada.chave !== nova.chave), nova]
    .sort((anterior, seguinte) => anterior.salvoEm - seguinte.salvoEm)
    .slice(-limite)
}

export function podeGuardar(resposta: unknown): boolean {
  if (Array.isArray(resposta)) return resposta.every(podeGuardar)
  if (resposta === null || typeof resposta !== 'object') return true
  if ('status_dado' in resposta && resposta.status_dado === 'fonte_indisponivel') return false
  return Object.values(resposta).every(podeGuardar)
}

export function montarChaveCache(
  rota: string,
  parametros: Record<string, string>,
  modo: Modo,
): string {
  const ordenados = Object.keys(parametros)
    .sort()
    .map((nome) => `${nome}=${parametros[nome]}`)
    .join('&')
  return `${modo}:${rota}?${ordenados}`
}
