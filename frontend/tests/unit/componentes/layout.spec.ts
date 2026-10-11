import { flushPromises, mount } from '@vue/test-utils'
import PrimeVue from 'primevue/config'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import periodos from '@mock/periodos.json'

const TEXTO_REAL =
  'Projeto acadêmico (UNIDAVI), sem vínculo com o Governo Federal. Os dados vêm da API pública do Portal da Transparência.'
const TEXTO_MOCK = 'Dados fictícios (modo de demonstração). Não use estes números para conferência.'

const global = { plugins: [[PrimeVue, { theme: 'none' }] as [typeof PrimeVue, object]] }

function simularSaude(resposta: () => Promise<Response>) {
  vi.stubGlobal('fetch', vi.fn<typeof fetch>(resposta))
}

async function montarBanner() {
  const { default: BannerAviso } = await import('@/componentes/layout/BannerAviso.vue')
  const { useModoMock } = await import('@/composables/useModoMock')
  const banner = mount(BannerAviso, { global })
  await useModoMock().carregar()
  await flushPromises()
  return banner
}

beforeEach(() => {
  vi.resetModules()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('BannerAviso', () => {
  it('avisa que os dados são fictícios no modo mock', async () => {
    simularSaude(async () => new Response(JSON.stringify({ modo_mock: true })))

    const banner = await montarBanner()

    expect(banner.text().replace(/\s+/g, ' ')).toContain(TEXTO_MOCK)
    expect(banner.classes()).toContain('banner--mock')
    expect(banner.attributes('role')).toBe('status')
  })

  it('avisa que o site não é oficial no modo real', async () => {
    simularSaude(async () => new Response(JSON.stringify({ modo_mock: false })))

    const banner = await montarBanner()

    expect(banner.text().replace(/\s+/g, ' ')).toContain(TEXTO_REAL)
    expect(banner.find('button').exists()).toBe(false)
  })

  it('mantém o aviso de site não oficial quando /health falha', async () => {
    simularSaude(async () => {
      throw new TypeError('Failed to fetch')
    })

    const banner = await montarBanner()

    expect(banner.text().replace(/\s+/g, ' ')).toContain(TEXTO_REAL)
  })
})

describe('RodapeFonte', () => {
  it('mostra o período vindo de /periodos e o aviso de site não oficial', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn<typeof fetch>(async () => new Response(JSON.stringify(periodos))),
    )
    const { default: RodapeFonte } = await import('@/componentes/layout/RodapeFonte.vue')
    const { usePeriodos } = await import('@/composables/usePeriodos')
    const rodape = mount(RodapeFonte)

    expect(rodape.text()).not.toContain('mar/2023')
    await usePeriodos().carregar()
    await flushPromises()

    expect(rodape.text()).toContain('Portal da Transparência (API de dados) · mar/2023 a ago/2026')
    expect(rodape.text()).toContain('não é um site oficial do governo')
  })
})
