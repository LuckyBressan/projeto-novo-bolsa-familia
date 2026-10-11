import { CODIGOS_FRONT, ErroConsulta } from './erros'

export interface OpcoesConsulta {
  controle: AbortController
  tempoLimiteMs: number
}

const BASE = '/api/v1'
const MOTIVO_TEMPO_ESGOTADO = 'tempo_esgotado'

function montarUrl(caminho: string, parametros: Record<string, string>): string {
  const consulta = new URLSearchParams(parametros).toString()
  return consulta ? `${BASE}${caminho}?${consulta}` : `${BASE}${caminho}`
}

async function lerEnvelopeErro(resposta: Response): Promise<ErroConsulta> {
  const corpo = await resposta.json().catch(() => null)
  const erro = corpo?.erro
  if (typeof erro?.codigo !== 'string') {
    return new ErroConsulta({ codigo: 'ERRO_INTERNO', httpStatus: resposta.status })
  }
  return new ErroConsulta({
    codigo: erro.codigo,
    httpStatus: resposta.status,
    correlacaoId: erro.correlacao_id,
    detalhes: erro.detalhes,
  })
}

function traduzirFalha(falha: unknown, sinal: AbortSignal): ErroConsulta {
  if (sinal.aborted && sinal.reason === MOTIVO_TEMPO_ESGOTADO) {
    return new ErroConsulta({ codigo: CODIGOS_FRONT.tempoEsgotado })
  }
  if (sinal.aborted) return new ErroConsulta({ codigo: CODIGOS_FRONT.cancelada })
  if (falha instanceof ErroConsulta) return falha
  return new ErroConsulta({ codigo: CODIGOS_FRONT.semConexao })
}

export async function obter<Resposta>(
  caminho: string,
  parametros: Record<string, string>,
  opcoes: OpcoesConsulta,
): Promise<Resposta> {
  const { controle, tempoLimiteMs } = opcoes
  const temporizador = setTimeout(() => controle.abort(MOTIVO_TEMPO_ESGOTADO), tempoLimiteMs)
  try {
    const resposta = await fetch(montarUrl(caminho, parametros), { signal: controle.signal })
    if (resposta.ok) return (await resposta.json()) as Resposta
    throw await lerEnvelopeErro(resposta)
  } catch (falha) {
    throw traduzirFalha(falha, controle.signal)
  } finally {
    clearTimeout(temporizador)
  }
}
