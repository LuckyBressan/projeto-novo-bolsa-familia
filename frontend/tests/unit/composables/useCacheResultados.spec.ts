import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import comparacaoFalhaFonte from '@mock/comparacao_4209102-x-4214805_2024-10a12_falha-fonte.json'
import comparacao from '@mock/comparacao_4214805-x-4202404_2024-01a03.json'
import { criarCacheResultados } from '@/composables/useCacheResultados'

const INICIO = new Date('2026-10-11T15:40:00')
const minutos = (quantidade: number) => quantidade * 60 * 1000

beforeEach(() => {
  vi.useFakeTimers()
  vi.setSystemTime(INICIO)
  sessionStorage.clear()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('cache de resultados na sessão', () => {
  it('devolve o resultado guardado enquanto ele tem menos de 1 hora', () => {
    const cache = criarCacheResultados(sessionStorage)
    cache.guardar('chave', comparacao)

    vi.advanceTimersByTime(minutos(59))
    expect(cache.ler('chave')).toEqual({
      chave: 'chave',
      salvoEm: INICIO.getTime(),
      dados: comparacao,
    })

    vi.advanceTimersByTime(minutos(2))
    expect(cache.ler('chave')).toBeNull()
    expect(cache.ler('outra')).toBeNull()
  })

  it('mantém o resultado depois de recarregar a página', () => {
    criarCacheResultados(sessionStorage).guardar('chave', comparacao)

    const recarregado = criarCacheResultados(sessionStorage)

    expect(recarregado.ler('chave')?.dados).toEqual(comparacao)
  })

  it('segue só com a memória quando o navegador bloqueia ou corrompe o armazenamento', () => {
    const bloqueado = {
      getItem: () => {
        throw new DOMException('bloqueado', 'SecurityError')
      },
      setItem: () => {
        throw new DOMException('cota cheia', 'QuotaExceededError')
      },
    } as unknown as Storage
    const cache = criarCacheResultados(bloqueado)
    cache.guardar('chave', comparacao)
    expect(cache.ler('chave')?.dados).toEqual(comparacao)

    sessionStorage.setItem('resultados', '{ não é json')
    expect(criarCacheResultados(sessionStorage).ler('chave')).toBeNull()
  })

  it('não guarda resposta com cidade de fonte indisponível, para permitir nova tentativa', () => {
    const cache = criarCacheResultados(sessionStorage)

    cache.guardar('chave', comparacaoFalhaFonte)

    expect(cache.ler('chave')).toBeNull()
  })

  it('lembra os últimos filtros de cada tela durante a sessão', () => {
    const filtros = { cidadeA: '4214805', cidadeB: '4202404', ano: 2024, mesInicio: 1, mesFim: 3 }
    criarCacheResultados(sessionStorage).guardarFiltros('comparacao', filtros)

    const recarregado = criarCacheResultados(sessionStorage)

    expect(recarregado.lerFiltros('comparacao')).toEqual(filtros)
    expect(recarregado.lerFiltros('capitais')).toBeNull()
  })
})
