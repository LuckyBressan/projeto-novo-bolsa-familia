import { readonly, ref } from 'vue'

import { buscarSaude } from '@/api/rotas'
import type { Fonte, Modo } from '@/api/tipos'

const modo = ref<Modo>('real')
let carregamento: Promise<void> | null = null

export function useModoMock() {
  function carregar(): Promise<void> {
    carregamento ??= buscarSaude()
      .then((saude) => {
        modo.value = saude.modo_mock ? 'mock' : 'real'
      })
      .catch(() => undefined)
    return carregamento
  }

  function registrarFonte(fonte: Fonte): void {
    if (fonte === 'mock') modo.value = 'mock'
  }

  return { modo: readonly(modo), carregar, registrarFonte }
}
