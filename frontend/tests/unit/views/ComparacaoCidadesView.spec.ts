import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import comparacao from '@mock/comparacao_4214805-x-4202404_2024-01a03.json'
import estados from '@mock/estados.json'
import evolucao from '@mock/evolucao_4214805-x-4202404_2024-01a03.json'
import saude from '@mock/health.json'
import municipiosSc from '@mock/municipios_uf-SC.json'
import periodos from '@mock/periodos.json'

const URL_COMPLETA = '/?cidadeA=4214805&cidadeB=4202404&ano=2024&mesInicio=1&mesFim=3'

const RESPOSTAS: Record<string, unknown> = {
  '/health': saude,
  '/periodos': periodos,
  '/estados': estados,
  '/municipios': municipiosSc,
  '/comparacoes/municipios': comparacao,
  '/evolucao-mensal': evolucao,
}

function simularApi(falhas: string[] = []) {
  const buscar = vi.fn<(url: string) => Promise<Response>>(async (url) => {
    const caminho = url.replace('/api/v1', '').split('?')[0] ?? ''
    if (falhas.includes(caminho)) return new Response('', { status: 502 })
    return new Response(JSON.stringify(RESPOSTAS[caminho]), { status: 200 })
  })
  vi.stubGlobal('fetch', buscar)
  return buscar
}

function listarChamadas(buscar: ReturnType<typeof simularApi>, trecho: string) {
  return buscar.mock.calls.map(([url]) => url).filter((url) => url.includes(trecho))
}

async function abrir(endereco: string) {
  const { default: PrimeVue } = await import('primevue/config')
  const { default: router } = await import('@/router')
  const { default: Tela } = await import('@/views/ComparacaoCidadesView.vue')
  const { usePeriodos } = await import('@/composables/usePeriodos')
  await router.push(endereco)
  await router.isReady()
  usePeriodos().carregar()
  const tela = mount(Tela, {
    global: { plugins: [router, [PrimeVue, { theme: 'none' }]], stubs: { Chart: true } },
    attachTo: document.body,
  })
  await flushPromises()
  return { tela, router, texto: () => tela.text().replace(/\s+/g, ' ') }
}

beforeEach(() => {
  vi.resetModules()
})

afterEach(() => {
  vi.unstubAllGlobals()
  document.body.innerHTML = ''
})

describe('tela Comparar cidades', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
  })

  it('ao abrir, carrega só os catálogos e explica por que o botão está desabilitado', async () => {
    const buscar = simularApi()

    const { tela, texto } = await abrir('/')

    expect(listarChamadas(buscar, '/comparacoes')).toEqual([])
    expect(listarChamadas(buscar, '/periodos')).toHaveLength(1)
    expect(tela.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(texto()).toContain('Escolha a cidade A')
    expect(texto()).toContain('Preencha os filtros e clique em Gerar comparativo.')
  })

  it('com filtros na URL, só consulta depois do clique em Gerar comparativo', async () => {
    const buscar = simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)

    expect(listarChamadas(buscar, '/comparacoes')).toEqual([])
    expect(tela.get('button[type="submit"]').attributes('disabled')).toBeUndefined()

    await tela.get('form').trigger('submit')
    await flushPromises()

    expect(listarChamadas(buscar, '/comparacoes')).toEqual([
      '/api/v1/comparacoes/municipios?codigo_ibge_a=4214805&codigo_ibge_b=4202404&ano=2024&mes_inicio=1&mes_fim=3',
    ])
    expect(texto()).toContain('Rio do Sul (SC) × Blumenau (SC) · jan/2024 a mar/2024 · 3 meses')
    expect(texto()).toContain('R$ 3.042.086,65')
    expect(texto()).toContain('Beneficiários (média mensal)')
    expect(texto()).toMatch(/Resultado consultado às \d{2}:\d{2}\./)
    expect(texto()).not.toContain('para consultar de novo')
    expect(document.activeElement?.id).toBe('secao-indicadores')
  })
})

describe('tela Comparar cidades com resultado em cache', () => {
  it('reabre a mesma URL com o resultado do cache, sem nova consulta', async () => {
    sessionStorage.clear()
    localStorage.clear()
    const primeira = simularApi()
    const original = await abrir(URL_COMPLETA)
    await original.tela.get('form').trigger('submit')
    await flushPromises()
    expect(listarChamadas(primeira, '/comparacoes')).toHaveLength(1)
    original.tela.unmount()

    vi.resetModules()
    const segunda = simularApi()
    const { texto } = await abrir(URL_COMPLETA)

    expect(listarChamadas(segunda, '/comparacoes')).toEqual([])
    expect(texto()).toContain('R$ 3.042.086,65')
    expect(texto()).toContain('Clique em Gerar comparativo para consultar de novo.')
  })

  it('avisa que os filtros mudaram sem consultar de novo', async () => {
    const buscar = simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)
    const { default: SeletorPeriodo } = await import('@/componentes/filtros/SeletorPeriodo.vue')

    tela.getComponent(SeletorPeriodo).vm.$emit('update:modelValue', {
      ano: 2024,
      mesInicio: 4,
      mesFim: 6,
    })
    await flushPromises()

    expect(texto()).toContain('Os filtros mudaram.')
    expect(texto()).toContain('ainda é de Rio do Sul (SC) × Blumenau (SC), jan/2024 a mar/2024')
    expect(listarChamadas(buscar, '/comparacoes')).toEqual([])
  })
})

describe('tela Comparar cidades: evolução mensal', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
  })

  it('consulta a evolução junto com a comparação e mostra as duas seções com tabela', async () => {
    const buscar = simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)

    expect(listarChamadas(buscar, '/evolucao-mensal')).toEqual([])

    await tela.get('form').trigger('submit')
    await flushPromises()

    expect(listarChamadas(buscar, '/evolucao-mensal')).toEqual([
      '/api/v1/evolucao-mensal?codigo_ibge_a=4214805&codigo_ibge_b=4202404&ano=2024&mes_inicio=1&mes_fim=3',
    ])
    expect(tela.findAll('h2').map((titulo) => titulo.text())).toEqual([
      'Indicadores do período',
      'Evolução do valor total',
      'Evolução dos beneficiários',
    ])
    expect(texto()).toContain('Variação em relação ao mês anterior')
    expect(texto()).toContain('▲ +16')
    expect(texto()).toContain('▼ −8')
    expect(texto()).toContain('R$ 1.013.272,42')
    expect(tela.findAll('details')).toHaveLength(2)
  })

  it('se só a evolução falhar, mantém os indicadores e refaz só a evolução', async () => {
    const buscar = simularApi(['/evolucao-mensal'])
    const { tela, texto } = await abrir(URL_COMPLETA)
    await tela.get('form').trigger('submit')
    await flushPromises()

    expect(texto()).toContain('R$ 3.042.086,65')
    expect(texto()).not.toContain('Variação em relação ao mês anterior')
    const repetir = tela.findAll('button').filter((botao) => botao.text() === 'Tentar novamente')
    expect(repetir).toHaveLength(2)

    await repetir[0]?.trigger('click')
    await flushPromises()

    expect(listarChamadas(buscar, '/evolucao-mensal')).toHaveLength(2)
    expect(listarChamadas(buscar, '/comparacoes')).toHaveLength(1)
  })
})
