import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'

import comparacaoParcial from '@mock/comparacao_4202404-x-4209102_2023-10a12_parcial.json'
import comparacao from '@mock/comparacao_4214805-x-4202404_2024-01a03.json'
import { CODIGOS_FRONT, ErroConsulta } from '@/api/erros'
import type { DefinicaoConsulta } from '@/api/rotas'
import type { Comparacao, Modo } from '@/api/tipos'
import { criarCacheResultados } from '@/composables/useCacheResultados'
import { useConsulta } from '@/composables/useConsulta'

interface Filtros {
  cidadeA: string
  cidadeB: string
}

const FILTROS: Filtros = { cidadeA: '4214805', cidadeB: '4202404' }
const OUTROS_FILTROS: Filtros = { cidadeA: '4202404', cidadeB: '4209102' }

function montarCenario() {
  const pendentes: Array<{
    resolver: (resposta: Comparacao) => void
    rejeitar: (erro: ErroConsulta) => void
  }> = []
  const buscar = vi.fn<DefinicaoConsulta<Filtros, Comparacao>['buscar']>(
    (_parametros, controle) =>
      new Promise<Comparacao>((resolver, rejeitar) => {
        pendentes.push({ resolver, rejeitar })
        controle.signal.addEventListener('abort', () =>
          rejeitar(new ErroConsulta({ codigo: CODIGOS_FRONT.cancelada })),
        )
      }),
  )
  const definicao: DefinicaoConsulta<Filtros, Comparacao> = {
    rota: '/comparacoes/municipios',
    montarParametros: (filtros) => ({ a: filtros.cidadeA, b: filtros.cidadeB }),
    buscar,
  }
  const dependencias = { cache: criarCacheResultados(sessionStorage), modo: ref<Modo>('mock') }
  return { definicao, dependencias, pendentes, buscar }
}

beforeEach(() => {
  sessionStorage.clear()
})

describe('useConsulta', () => {
  it('marca o carregamento e entrega os dados com a hora da consulta', async () => {
    const { definicao, dependencias, pendentes } = montarCenario()
    const consulta = useConsulta(definicao, dependencias)

    const execucao = consulta.executar(FILTROS)
    expect(consulta.carregando.value).toBe(true)
    pendentes[0]?.resolver(comparacao as Comparacao)
    await execucao

    expect(consulta.carregando.value).toBe(false)
    expect(consulta.dados.value).toEqual(comparacao)
    expect(consulta.filtrosResultado.value).toEqual(FILTROS)
    expect(consulta.consultadoEm.value).toBeTypeOf('number')
    expect(consulta.origemCache.value).toBe(false)
    expect(consulta.erro.value).toBeNull()
  })

  it('cancela a consulta anterior e descarta a resposta dela', async () => {
    const { definicao, dependencias, pendentes, buscar } = montarCenario()
    const consulta = useConsulta(definicao, dependencias)

    const antiga = consulta.executar(FILTROS)
    const nova = consulta.executar(OUTROS_FILTROS)
    expect(buscar.mock.calls[0]?.[1].signal.aborted).toBe(true)

    pendentes[1]?.resolver(comparacaoParcial as Comparacao)
    pendentes[0]?.resolver(comparacao as Comparacao)
    await Promise.all([antiga, nova])

    expect(consulta.dados.value).toEqual(comparacaoParcial)
    expect(consulta.filtrosResultado.value).toEqual(OUTROS_FILTROS)
    expect(consulta.erro.value).toBeNull()
    expect(consulta.carregando.value).toBe(false)
  })

  it('guarda o erro, limpa o resultado e não tenta de novo sozinho', async () => {
    vi.useFakeTimers()
    const { definicao, dependencias, pendentes, buscar } = montarCenario()
    const consulta = useConsulta(definicao, dependencias)
    const execucao = consulta.executar(FILTROS)
    pendentes[0]?.resolver(comparacao as Comparacao)
    await execucao

    const falha = consulta.executar(OUTROS_FILTROS)
    pendentes[1]?.rejeitar(new ErroConsulta({ codigo: 'FONTE_INDISPONIVEL', httpStatus: 503 }))
    await falha
    await vi.advanceTimersByTimeAsync(120_000)
    vi.useRealTimers()

    expect(consulta.erro.value).toMatchObject({ codigo: 'FONTE_INDISPONIVEL' })
    expect(consulta.dados.value).toBeNull()
    expect(consulta.carregando.value).toBe(false)
    expect(buscar).toHaveBeenCalledTimes(2)
  })

  it('volta ao resultado anterior, sem erro, quando o usuário cancela', async () => {
    const { definicao, dependencias, pendentes } = montarCenario()
    const consulta = useConsulta(definicao, dependencias)
    const execucao = consulta.executar(FILTROS)
    pendentes[0]?.resolver(comparacao as Comparacao)
    await execucao

    const cancelada = consulta.executar(OUTROS_FILTROS)
    consulta.cancelar()
    await cancelada

    expect(consulta.carregando.value).toBe(false)
    expect(consulta.erro.value).toBeNull()
    expect(consulta.dados.value).toEqual(comparacao)
    expect(consulta.filtrosResultado.value).toEqual(FILTROS)
  })

  it('restaura do cache o resultado já consultado, sem chamar a API', async () => {
    const original = montarCenario()
    const consulta = useConsulta(original.definicao, original.dependencias)
    const execucao = consulta.executar(FILTROS)
    original.pendentes[0]?.resolver(comparacao as Comparacao)
    await execucao

    const recarregado = montarCenario()
    const restaurada = useConsulta(recarregado.definicao, recarregado.dependencias)

    expect(restaurada.restaurar(OUTROS_FILTROS)).toBe(false)
    expect(restaurada.dados.value).toBeNull()
    expect(restaurada.restaurar(FILTROS)).toBe(true)
    expect(restaurada.dados.value).toEqual(comparacao)
    expect(restaurada.filtrosResultado.value).toEqual(FILTROS)
    expect(restaurada.origemCache.value).toBe(true)
    expect(restaurada.consultadoEm.value).toBe(consulta.consultadoEm.value)
    expect(recarregado.buscar).not.toHaveBeenCalled()

    recarregado.dependencias.modo.value = 'real'
    const outroModo = useConsulta(recarregado.definicao, recarregado.dependencias)
    expect(outroModo.restaurar(FILTROS)).toBe(false)
  })
})
