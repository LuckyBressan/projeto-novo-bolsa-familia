import {
  adicionarEntrada,
  conferirValidade,
  podeGuardar,
  VALIDADE_RESULTADO_MS,
  type EntradaCache,
} from '@/dominio/cache'
import { gravarJson, lerJson, obterArmazenamento } from './armazenamento'

export type Tela = 'comparacao' | 'capitais'

const CHAVE_RESULTADOS = 'resultados'
const CHAVE_FILTROS = 'filtros'

export function criarCacheResultados(armazenamento: Storage | null) {
  let entradas = lerJson<EntradaCache[]>(armazenamento, CHAVE_RESULTADOS) ?? []
  const memoriaFiltros = new Map<Tela, unknown>()

  function ler(chave: string): EntradaCache | null {
    const entrada = entradas.find((item) => item.chave === chave)
    if (!entrada) return null
    return conferirValidade(entrada.salvoEm, Date.now(), VALIDADE_RESULTADO_MS) ? entrada : null
  }

  function guardar(chave: string, dados: unknown, salvoEm: number = Date.now()): void {
    entradas = podeGuardar(dados)
      ? adicionarEntrada(entradas, { chave, salvoEm, dados })
      : entradas.filter((item) => item.chave !== chave)
    gravarJson(armazenamento, CHAVE_RESULTADOS, entradas)
  }

  function lerFiltros<Filtros>(tela: Tela): Filtros | null {
    const guardados =
      memoriaFiltros.get(tela) ?? lerJson<Filtros>(armazenamento, `${CHAVE_FILTROS}:${tela}`)
    return (guardados as Filtros | undefined) ?? null
  }

  function guardarFiltros(tela: Tela, filtros: unknown): void {
    memoriaFiltros.set(tela, filtros)
    gravarJson(armazenamento, `${CHAVE_FILTROS}:${tela}`, filtros)
  }

  return { ler, guardar, lerFiltros, guardarFiltros }
}

export type CacheResultados = ReturnType<typeof criarCacheResultados>

let cacheSessao: CacheResultados | null = null

export function useCacheResultados(): CacheResultados {
  cacheSessao ??= criarCacheResultados(obterArmazenamento('sessionStorage'))
  return cacheSessao
}
