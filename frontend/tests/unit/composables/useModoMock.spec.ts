import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import saude from '@mock/health.json'

function responder(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), { status })
}

async function importar() {
  const { useModoMock } = await import('@/composables/useModoMock')
  return useModoMock()
}

beforeEach(() => {
  vi.resetModules()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('modo mock', () => {
  it('lê /health uma única vez e marca o modo mock', async () => {
    const buscar = vi.fn<typeof fetch>().mockImplementation(async () => responder(saude))
    vi.stubGlobal('fetch', buscar)
    const { modo, carregar } = await importar()

    expect(modo.value).toBe('real')
    await Promise.all([carregar(), carregar()])

    expect(modo.value).toBe('mock')
    expect(buscar).toHaveBeenCalledTimes(1)
    expect(buscar.mock.calls[0]?.[0]).toBe('/api/v1/health')
  })

  it('fica no modo real quando /health falha, sem propagar o erro', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    const { modo, carregar } = await importar()

    await expect(carregar()).resolves.toBeUndefined()

    expect(modo.value).toBe('real')
  })

  it('passa para o modo mock quando uma resposta chega com a fonte mock', async () => {
    const { modo, registrarFonte } = await importar()

    registrarFonte('portal_transparencia')
    expect(modo.value).toBe('real')

    registrarFonte('mock')
    expect(modo.value).toBe('mock')
  })
})
