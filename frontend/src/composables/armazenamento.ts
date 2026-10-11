export function obterArmazenamento(tipo: 'localStorage' | 'sessionStorage'): Storage | null {
  try {
    return window[tipo]
  } catch {
    return null
  }
}

export function lerJson<Valor>(armazenamento: Storage | null, chave: string): Valor | null {
  try {
    const texto = armazenamento?.getItem(chave)
    return texto ? (JSON.parse(texto) as Valor) : null
  } catch {
    return null
  }
}

export function gravarJson(armazenamento: Storage | null, chave: string, valor: unknown): void {
  try {
    armazenamento?.setItem(chave, JSON.stringify(valor))
  } catch {
    return
  }
}
