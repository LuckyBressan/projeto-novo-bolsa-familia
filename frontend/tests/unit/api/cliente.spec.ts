import { afterEach, describe, expect, it, vi } from 'vitest'

import erroIntervalo from '@mock/erro_intervalo-maior-que-3-meses.json'
import periodos from '@mock/periodos.json'
import { obter } from '@/api/cliente'
import { CODIGOS_FRONT, ErroConsulta } from '@/api/erros'

function responder(corpo: unknown, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function esperarAborto(_url: string, configuracao: RequestInit) {
  return new Promise<Response>((_resolver, rejeitar) => {
    configuracao.signal?.addEventListener('abort', () =>
      rejeitar(new DOMException('Aborted', 'AbortError')),
    )
  })
}

function opcoes(tempoLimiteMs = 1000) {
  return { controle: new AbortController(), tempoLimiteMs }
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('cliente da API', () => {
  it('chama o caminho relativo com os parâmetros e devolve o JSON', async () => {
    const buscar = vi.fn<typeof fetch>().mockResolvedValue(responder(periodos))
    vi.stubGlobal('fetch', buscar)

    const resposta = await obter('/municipios', { uf: 'SC' }, opcoes())

    expect(resposta).toEqual(periodos)
    expect(buscar.mock.calls[0]?.[0]).toBe('/api/v1/municipios?uf=SC')
  })

  it('transforma o envelope de erro do back-end em ErroConsulta', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(responder(erroIntervalo, 422)))

    const erro = await obter('/evolucao-mensal', {}, opcoes()).catch((falha) => falha)

    expect(erro).toBeInstanceOf(ErroConsulta)
    expect(erro).toMatchObject({
      codigo: 'PERIODO_INVALIDO',
      httpStatus: 422,
      correlacaoId: 'exemplo-0000',
      detalhes: { max_meses_intervalo: 3 },
    })
  })

  it('trata resposta de erro sem o envelope como erro interno', async () => {
    const pagina = new Response('<html>502 Bad Gateway</html>', { status: 502 })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(pagina))

    const erro = await obter('/periodos', {}, opcoes()).catch((falha) => falha)

    expect(erro).toBeInstanceOf(ErroConsulta)
    expect(erro).toMatchObject({ codigo: 'ERRO_INTERNO', httpStatus: 502, correlacaoId: null })
  })

  it('aborta ao passar do tempo limite e avisa que o tempo esgotou', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn(esperarAborto))

    const consulta = obter('/capitais/comparacao', {}, opcoes(90_000)).catch((falha) => falha)
    await vi.advanceTimersByTimeAsync(90_000)

    expect(await consulta).toMatchObject({ codigo: CODIGOS_FRONT.tempoEsgotado })
  })

  it('avisa que foi cancelada quando o controle é abortado pelo usuário', async () => {
    vi.stubGlobal('fetch', vi.fn(esperarAborto))
    const configuracao = opcoes()

    const consulta = obter('/evolucao-mensal', {}, configuracao).catch((falha) => falha)
    configuracao.controle.abort()

    expect(await consulta).toMatchObject({ codigo: CODIGOS_FRONT.cancelada, cancelada: true })
  })

  it('avisa que está sem conexão quando a chamada nem chega ao servidor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    const erro = await obter('/periodos', {}, opcoes()).catch((falha) => falha)

    expect(erro).toBeInstanceOf(ErroConsulta)
    expect(erro).toMatchObject({ codigo: CODIGOS_FRONT.semConexao, httpStatus: null })
  })
})
