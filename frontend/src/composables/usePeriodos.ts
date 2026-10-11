import { ref, shallowRef } from 'vue'

import { ErroConsulta } from '@/api/erros'
import { buscarPeriodos } from '@/api/rotas'
import type { Periodos } from '@/api/tipos'

const periodos = shallowRef<Periodos | null>(null)
const erro = shallowRef<ErroConsulta | null>(null)
const carregando = ref(false)
let carga: Promise<void> | null = null

async function buscar(): Promise<void> {
  carregando.value = true
  erro.value = null
  try {
    periodos.value = await buscarPeriodos()
  } catch (falha) {
    erro.value =
      falha instanceof ErroConsulta ? falha : new ErroConsulta({ codigo: 'ERRO_INTERNO' })
    carga = null
  } finally {
    carregando.value = false
  }
}

export function usePeriodos() {
  function carregar(): Promise<void> {
    carga ??= buscar()
    return carga
  }

  return { periodos, erro, carregando, carregar }
}
