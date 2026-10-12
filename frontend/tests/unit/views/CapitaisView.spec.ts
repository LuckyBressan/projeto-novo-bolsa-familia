import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import capitais from '@mock/capitais_ref-4214805_2024-01a03_todas.json'
import estados from '@mock/estados.json'
import saude from '@mock/health.json'
import municipiosSc from '@mock/municipios_uf-SC.json'
import periodos from '@mock/periodos.json'

const URL_COMPLETA = '/capitais?referencia=4214805&ano=2024&mesInicio=1&mesFim=3'
const CINCO_CAPITAIS = ['3550308', '3304557', '2927408', '2304400', '1302603']

const RESPOSTAS: Record<string, unknown> = {
  '/health': saude,
  '/periodos': periodos,
  '/estados': estados,
  '/municipios': municipiosSc,
  '/capitais/comparacao': capitais,
}

function simularApi() {
  const buscar = vi.fn<(url: string) => Promise<Response>>(async (url) => {
    const caminho = url.replace('/api/v1', '').split('?')[0] ?? ''
    return new Response(JSON.stringify(RESPOSTAS[caminho]), { status: 200 })
  })
  vi.stubGlobal('fetch', buscar)
  return buscar
}

function listarConsultas(buscar: ReturnType<typeof simularApi>) {
  return buscar.mock.calls.map(([url]) => url).filter((url) => url.includes('/capitais/'))
}

async function abrir(endereco: string) {
  const { default: PrimeVue } = await import('primevue/config')
  const { default: router } = await import('@/router')
  const { default: Tela } = await import('@/views/CapitaisView.vue')
  const { usePeriodos } = await import('@/composables/usePeriodos')
  await router.push(endereco)
  await router.isReady()
  usePeriodos().carregar()
  const tela = mount(Tela, {
    global: { plugins: [router, [PrimeVue, { theme: 'none' }]], stubs: { Chart: true } },
    attachTo: document.body,
  })
  await flushPromises()
  return { tela, texto: () => tela.text().replace(/\s+/g, ' ') }
}

async function gerar(tela: Awaited<ReturnType<typeof abrir>>['tela']) {
  await tela.get('form').trigger('submit')
  await flushPromises()
}

beforeEach(() => {
  vi.resetModules()
  sessionStorage.clear()
  localStorage.clear()
})

afterEach(() => {
  vi.unstubAllGlobals()
  document.body.innerHTML = ''
})

describe('tela Capitais', () => {
  it('ao abrir, não consulta e explica por que o botão está desabilitado', async () => {
    const buscar = simularApi()

    const { tela, texto } = await abrir('/capitais')

    expect(listarConsultas(buscar)).toEqual([])
    expect(tela.get('button[type="submit"]').attributes('disabled')).toBeDefined()
    expect(texto()).toContain('Escolha o município de referência')
    expect(texto()).toContain('Preencha os filtros e clique em Gerar comparativo.')
  })

  it('uma consulta alimenta as quatro seções, com a referência no ranking', async () => {
    const buscar = simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)

    expect(listarConsultas(buscar)).toEqual([])

    await gerar(tela)

    expect(listarConsultas(buscar)).toEqual([
      '/api/v1/capitais/comparacao?codigo_ibge_referencia=4214805&ano=2024&mes_inicio=1&mes_fim=3&metrica=valor_total',
    ])
    expect(tela.findAll('h2').map((titulo) => titulo.text())).toEqual([
      'Posição do município',
      'Ranking das capitais',
      'Evolução mensal',
      'Tabela detalhada por capital',
    ])
    expect(texto()).toContain('Rio do Sul (SC) · jan/2024 a mar/2024 · todas as 27 capitais')
    expect(texto()).toContain(
      'Ficaria em 27º lugar, depois das 26 capitais ranqueadas por valor total recebido.',
    )
    expect(texto()).toContain('Sem posição no ranking: Boa Vista (sem dados).')
    expect(texto()).toContain('R$ 1.384.095.675,14')
    expect(document.activeElement?.id).toBe('secao-posicao')
  })

  it('trocar a métrica só avisa que os filtros mudaram', async () => {
    const buscar = simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)
    await gerar(tela)
    const { default: SeletorMetrica } = await import('@/componentes/filtros/SeletorMetrica.vue')

    tela.getComponent(SeletorMetrica).vm.$emit('update:modelValue', 'valor_medio_por_beneficiario')
    await flushPromises()

    expect(texto()).toContain('Os filtros mudaram.')
    expect(texto()).toContain(
      'ainda é de Rio do Sul (SC), jan/2024 a mar/2024, valor total recebido',
    )
    expect(listarConsultas(buscar)).toHaveLength(1)
  })
})

describe('tela Capitais: capitais no gráfico de evolução', () => {
  it('começa pela capital da UF da referência e troca as capitais sem consultar', async () => {
    const buscar = simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)
    await gerar(tela)
    const { default: Seletor } = await import('@/componentes/resumo/SeletorCapitaisGrafico.vue')
    const { default: Grafico } = await import('@/componentes/resultados/GraficoEvolucao.vue')
    const listarSeries = () =>
      tela
        .getComponent(Grafico)
        .props('series')
        .map((serie) => [serie.nome, serie.posicao])

    expect(listarSeries()).toEqual([
      ['Rio do Sul (referência)', 1],
      ['Florianópolis (SC)', 0],
    ])
    expect(texto()).not.toContain('Até 5 capitais no gráfico.')

    tela.getComponent(Seletor).vm.$emit('update:modelValue', CINCO_CAPITAIS)
    await flushPromises()

    expect(listarSeries()).toEqual([
      ['Rio do Sul (referência)', 1],
      ['São Paulo (SP)', 0],
      ['Rio de Janeiro (RJ)', 2],
      ['Salvador (BA)', 3],
      ['Fortaleza (CE)', 4],
      ['Manaus (AM)', 5],
    ])
    expect(texto()).toContain('Até 5 capitais no gráfico.')

    tela.getComponent(Seletor).vm.$emit('update:modelValue', CINCO_CAPITAIS.slice(1))
    await flushPromises()

    expect(listarSeries()).toEqual([
      ['Rio do Sul (referência)', 1],
      ['Rio de Janeiro (RJ)', 2],
      ['Salvador (BA)', 3],
      ['Fortaleza (CE)', 4],
      ['Manaus (AM)', 5],
    ])
    expect(listarConsultas(buscar)).toHaveLength(1)
  })
})

describe('tela Capitais: cancelamento', () => {
  it('cancelar durante a consulta volta ao estado anterior, sem erro', async () => {
    simularApi()
    const { tela, texto } = await abrir(URL_COMPLETA)
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url: string, opcoes?: RequestInit) =>
          new Promise<Response>((_resolver, rejeitar) => {
            opcoes?.signal?.addEventListener('abort', () =>
              rejeitar(new DOMException('cancelada', 'AbortError')),
            )
          }),
      ),
    )

    await tela.get('form').trigger('submit')
    await flushPromises()
    expect(texto()).toContain('Consultando o Portal da Transparência…')

    const cancelar = tela.findAll('button').find((botao) => botao.text() === 'Cancelar')
    await cancelar?.trigger('click')
    await flushPromises()

    expect(texto()).not.toContain('Consultando o Portal da Transparência…')
    expect(texto()).toContain('Preencha os filtros e clique em Gerar comparativo.')
    expect(texto()).not.toContain('Tentar novamente')
  })
})
