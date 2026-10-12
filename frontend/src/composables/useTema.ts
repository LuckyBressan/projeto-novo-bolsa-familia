import { computed, ref, watch } from 'vue'

import {
  lerEscolha,
  listarClasses,
  resolverTema,
  type EscolhaTema,
  type PreferenciaSistema,
} from '@/dominio/tema'
import { obterArmazenamento } from './armazenamento'

interface AmbienteTema {
  armazenamento: Storage | null
  raiz: HTMLElement
  consultar(consulta: string): MediaQueryList | undefined
}

const CONSULTAS: Record<keyof PreferenciaSistema, string> = {
  contraste: '(prefers-contrast: more)',
  escuro: '(prefers-color-scheme: dark)',
}

const CLASSES_TEMA = ['tema-escuro', 'alto-contraste']
const CHAVE_TEMA = 'tema'

function lerGuardada(armazenamento: Storage | null): EscolhaTema {
  try {
    return lerEscolha(armazenamento?.getItem(CHAVE_TEMA))
  } catch {
    return 'automatico'
  }
}

export function criarTema(ambiente: AmbienteTema) {
  const escolha = ref<EscolhaTema>(lerGuardada(ambiente.armazenamento))
  const sistema = ref<PreferenciaSistema>({ contraste: false, escuro: false })

  for (const preferencia of Object.keys(CONSULTAS) as (keyof PreferenciaSistema)[]) {
    const consulta = ambiente.consultar(CONSULTAS[preferencia])
    sistema.value[preferencia] = consulta?.matches ?? false
    consulta?.addEventListener('change', (evento) => {
      sistema.value[preferencia] = evento.matches
    })
  }

  const tema = computed(() => resolverTema(escolha.value, sistema.value))

  watch(
    tema,
    (atual) => {
      ambiente.raiz.classList.remove(...CLASSES_TEMA)
      ambiente.raiz.classList.add(...listarClasses(atual))
    },
    { immediate: true },
  )

  function escolher(nova: EscolhaTema): void {
    escolha.value = nova
    try {
      ambiente.armazenamento?.setItem(CHAVE_TEMA, nova)
    } catch {
      return
    }
  }

  return { escolha, tema, escolher }
}

let compartilhado: ReturnType<typeof criarTema> | undefined

export function useTema() {
  compartilhado ??= criarTema({
    armazenamento: obterArmazenamento('localStorage'),
    raiz: document.documentElement,
    consultar: (consulta) => window.matchMedia?.(consulta),
  })
  return compartilhado
}
