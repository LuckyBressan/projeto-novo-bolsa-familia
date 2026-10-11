import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import periodosMock from '@mock/periodos.json'

async function importar() {
  const { usePeriodos } = await import('@/composables/usePeriodos')
  return usePeriodos()
}

beforeEach(() => {
  vi.resetModules()
  localStorage.clear()
  sessionStorage.clear()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('períodos', () => {
  it('carrega /periodos uma vez e guarda só na memória', async () => {
    const buscar = vi.fn<typeof fetch>(async () => new Response(JSON.stringify(periodosMock)))
    vi.stubGlobal('fetch', buscar)
    const { periodos, carregar } = await importar()

    await Promise.all([carregar(), carregar()])
    await (await importar()).carregar()

    expect(periodos.value).toEqual(periodosMock)
    expect(buscar).toHaveBeenCalledTimes(1)
    expect(localStorage.length + sessionStorage.length).toBe(0)
  })

  it('expõe o erro da carga e permite tentar de novo', async () => {
    const buscar = vi
      .fn<typeof fetch>()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockImplementation(async () => new Response(JSON.stringify(periodosMock)))
    vi.stubGlobal('fetch', buscar)
    const { periodos, erro, carregar } = await importar()

    await carregar()
    expect(erro.value).toMatchObject({ codigo: 'SEM_CONEXAO' })
    expect(periodos.value).toBeNull()

    await carregar()
    expect(erro.value).toBeNull()
    expect(periodos.value).toEqual(periodosMock)
  })
})
