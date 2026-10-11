import { formatarMes } from '@/dominio/formatacao'
import type { Periodos } from './tipos'

export type AcaoErro = 'revisar_filtros' | 'tentar_novamente'

export interface DescricaoErro {
  mensagem: string
  acao: AcaoErro
}

interface DadosErro {
  codigo: string
  httpStatus?: number | null
  correlacaoId?: string | null
  detalhes?: Record<string, unknown>
}

export const CODIGOS_FRONT = {
  tempoEsgotado: 'TEMPO_ESGOTADO',
  semConexao: 'SEM_CONEXAO',
  cancelada: 'CANCELADA',
} as const

export class ErroConsulta extends Error {
  readonly codigo: string
  readonly httpStatus: number | null
  readonly correlacaoId: string | null
  readonly detalhes: Record<string, unknown>

  constructor(dados: DadosErro) {
    super(dados.codigo)
    this.name = 'ErroConsulta'
    this.codigo = dados.codigo
    this.httpStatus = dados.httpStatus ?? null
    this.correlacaoId = dados.correlacaoId ?? null
    this.detalhes = dados.detalhes ?? {}
  }

  get cancelada(): boolean {
    return this.codigo === CODIGOS_FRONT.cancelada
  }
}

const DESCRICOES: Record<string, DescricaoErro> = {
  PARAMETRO_INVALIDO: {
    mensagem: 'Algum filtro está incompleto ou inválido. Revise os campos destacados.',
    acao: 'revisar_filtros',
  },
  ESTADO_INVALIDO: { mensagem: 'Estado não reconhecido.', acao: 'revisar_filtros' },
  MUNICIPIO_INVALIDO: { mensagem: 'Município não encontrado.', acao: 'revisar_filtros' },
  METRICA_INVALIDA: { mensagem: 'Métrica de ranking não reconhecida.', acao: 'revisar_filtros' },
  FONTE_INDISPONIVEL: {
    mensagem: 'O Portal da Transparência não respondeu agora. Tente novamente em alguns instantes.',
    acao: 'tentar_novamente',
  },
  LIMITE_FONTE_EXCEDIDO: {
    mensagem: 'Muitas consultas ao Portal em pouco tempo. Aguarde um minuto e tente novamente.',
    acao: 'tentar_novamente',
  },
  RESPOSTA_FONTE_INVALIDA: {
    mensagem: 'O Portal respondeu de forma inesperada.',
    acao: 'tentar_novamente',
  },
  [CODIGOS_FRONT.tempoEsgotado]: {
    mensagem: 'A consulta demorou mais que o esperado.',
    acao: 'tentar_novamente',
  },
  [CODIGOS_FRONT.semConexao]: {
    mensagem: 'Não foi possível falar com o servidor do sistema.',
    acao: 'tentar_novamente',
  },
}

const DESCRICAO_GENERICA: DescricaoErro = {
  mensagem: 'Ocorreu um erro inesperado.',
  acao: 'tentar_novamente',
}

function descreverPeriodoInvalido(periodos: Periodos | null): DescricaoErro {
  const regra = periodos
    ? `Escolha de 1 a ${periodos.max_meses_intervalo} meses do mesmo ano, entre ${formatarMes(periodos.periodo_min)} e ${formatarMes(periodos.periodo_max)}.`
    : 'Escolha um intervalo de até 3 meses do mesmo ano.'
  return { mensagem: regra, acao: 'revisar_filtros' }
}

export function descreverErro(erro: ErroConsulta, periodos: Periodos | null = null): DescricaoErro {
  if (erro.codigo === 'PERIODO_INVALIDO') return descreverPeriodoInvalido(periodos)
  return DESCRICOES[erro.codigo] ?? DESCRICAO_GENERICA
}
