import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useTelaEstreita(larguraMaxima = 575) {
  const estreita = ref(false)
  let consulta: MediaQueryList | undefined

  function atualizar() {
    estreita.value = consulta?.matches ?? false
  }

  onMounted(() => {
    consulta = window.matchMedia?.(`(max-width: ${larguraMaxima}px)`)
    consulta?.addEventListener('change', atualizar)
    atualizar()
  })

  onBeforeUnmount(() => consulta?.removeEventListener('change', atualizar))

  return estreita
}
