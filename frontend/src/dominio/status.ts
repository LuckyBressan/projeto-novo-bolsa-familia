import type { Indicadores, StatusDado } from '@/api/tipos'

export type SeveridadeSelo = 'success' | 'warn' | 'secondary' | 'danger'

export interface DescricaoStatus {
  severidade: SeveridadeSelo
  icone: string
  rotulo: string
  mensagem: string | null
}

type Situacao = Pick<Indicadores, 'status_dado' | 'meses_com_dados' | 'meses_solicitados'>

const DESCRICOES: Record<Exclude<StatusDado, 'parcial'>, DescricaoStatus> = {
  disponivel: {
    severidade: 'success',
    icone: 'pi pi-check',
    rotulo: 'Disponível',
    mensagem: null,
  },
  sem_dados: {
    severidade: 'secondary',
    icone: 'pi pi-minus',
    rotulo: 'Sem dados',
    mensagem: 'Sem dados para este período.',
  },
  fonte_indisponivel: {
    severidade: 'danger',
    icone: 'pi pi-times',
    rotulo: 'Fonte indisponível',
    mensagem: 'Não foi possível consultar esta cidade agora.',
  },
}

export function descreverStatus(situacao: Situacao): DescricaoStatus {
  if (situacao.status_dado !== 'parcial') return DESCRICOES[situacao.status_dado]
  const proporcao = `${situacao.meses_com_dados} de ${situacao.meses_solicitados} meses`
  return {
    severidade: 'warn',
    icone: 'pi pi-exclamation-triangle',
    rotulo: `Parcial · ${proporcao}`,
    mensagem: `Dados de ${proporcao}. Os valores consideram só os meses com dados.`,
  }
}
