import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'

import estados from '@mock/estados.json'
import municipiosSc from '@mock/municipios_uf-SC.json'
import type { Modo } from '@/api/tipos'
import { criarCatalogo, VERSAO_CATALOGO } from '@/composables/useCatalogo'

const INICIO = new Date('2026-10-11T15:40:00')
const dias = (quantidade: number) => quantidade * 24 * 60 * 60 * 1000

function simularApi() {
  const buscar = vi.fn<(url: string) => Promise<Response>>(async (url) => {
    const corpo = url.includes('/estados') ? estados : municipiosSc
    return new Response(JSON.stringify(corpo), { status: 200 })
  })
  vi.stubGlobal('fetch', buscar)
  return buscar
}

function abrirCatalogo(modo: Modo = 'mock') {
  return criarCatalogo({ armazenamento: localStorage, modo: ref(modo) })
}

beforeEach(() => {
  vi.useFakeTimers()
  vi.setSystemTime(INICIO)
  localStorage.clear()
})

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

describe('catálogos', () => {
  it('usa as UFs guardadas por 29 dias e pede de novo depois de 31', async () => {
    const buscar = simularApi()
    expect(await abrirCatalogo().carregarEstados()).toEqual(estados.items)
    expect(buscar).toHaveBeenCalledTimes(1)

    vi.setSystemTime(INICIO.getTime() + dias(29))
    expect(await abrirCatalogo().carregarEstados()).toEqual(estados.items)
    expect(buscar).toHaveBeenCalledTimes(1)

    vi.setSystemTime(INICIO.getTime() + dias(31))
    await abrirCatalogo().carregarEstados()
    expect(buscar).toHaveBeenCalledTimes(2)
  })

  it('guarda os municípios por UF e por modo, com a UF inteira numa requisição', async () => {
    const buscar = simularApi()
    expect(await abrirCatalogo('mock').carregarMunicipios('SC')).toEqual(municipiosSc.items)
    expect(buscar.mock.calls[0]?.[0]).toBe('/api/v1/municipios?uf=SC')

    vi.setSystemTime(INICIO.getTime() + dias(29))
    expect(await abrirCatalogo('mock').carregarMunicipios('SC')).toEqual(municipiosSc.items)
    expect(buscar).toHaveBeenCalledTimes(1)

    await abrirCatalogo('real').carregarMunicipios('SC')
    expect(buscar).toHaveBeenCalledTimes(2)

    await abrirCatalogo('mock').carregarMunicipios('PR')
    expect(buscar).toHaveBeenCalledTimes(3)
  })

  it('funciona só com a memória quando o navegador bloqueia o armazenamento', async () => {
    const buscar = simularApi()
    const bloqueado = {
      getItem: () => {
        throw new DOMException('bloqueado', 'SecurityError')
      },
      setItem: () => {
        throw new DOMException('cota cheia', 'QuotaExceededError')
      },
    } as unknown as Storage
    const catalogo = criarCatalogo({ armazenamento: bloqueado, modo: ref<Modo>('mock') })

    const [primeira, simultanea] = await Promise.all([
      catalogo.carregarMunicipios('SC'),
      catalogo.carregarMunicipios('SC'),
    ])
    const repetida = await catalogo.carregarMunicipios('SC')

    expect(primeira).toEqual(municipiosSc.items)
    expect(simultanea).toEqual(municipiosSc.items)
    expect(repetida).toEqual(municipiosSc.items)
    expect(buscar).toHaveBeenCalledTimes(1)
  })

  it('descarta o catálogo guardado por uma versão diferente do front', async () => {
    const buscar = simularApi()
    localStorage.setItem(
      'catalogo:estados',
      JSON.stringify({ salvoEm: INICIO.getTime(), versao: VERSAO_CATALOGO + 1, dados: [] }),
    )

    expect(await abrirCatalogo().carregarEstados()).toEqual(estados.items)
    expect(buscar).toHaveBeenCalledTimes(1)
    expect(JSON.parse(localStorage.getItem('catalogo:estados') ?? '{}').versao).toBe(
      VERSAO_CATALOGO,
    )
  })
})
