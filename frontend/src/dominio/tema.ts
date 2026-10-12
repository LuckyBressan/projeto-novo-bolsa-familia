export type Tema = 'claro' | 'escuro' | 'contraste'
export type EscolhaTema = 'automatico' | Tema

export interface PreferenciaSistema {
  contraste: boolean
  escuro: boolean
}

export function resolverTema(escolha: EscolhaTema, sistema: PreferenciaSistema): Tema {
  if (escolha !== 'automatico') return escolha
  if (sistema.contraste) return 'contraste'
  return sistema.escuro ? 'escuro' : 'claro'
}

export const OPCOES_TEMA: { valor: EscolhaTema; rotulo: string }[] = [
  { valor: 'automatico', rotulo: 'Automático' },
  { valor: 'claro', rotulo: 'Claro' },
  { valor: 'escuro', rotulo: 'Escuro' },
  { valor: 'contraste', rotulo: 'Alto contraste' },
]

export function lerEscolha(valor: unknown): EscolhaTema {
  return OPCOES_TEMA.find((opcao) => opcao.valor === valor)?.valor ?? 'automatico'
}

const CLASSES: Record<Tema, string[]> = {
  claro: [],
  escuro: ['tema-escuro'],
  contraste: ['tema-escuro', 'alto-contraste'],
}

export function listarClasses(tema: Tema): string[] {
  return CLASSES[tema]
}
