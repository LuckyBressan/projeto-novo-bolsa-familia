<script setup lang="ts">
import type { ErroConsulta } from '@/api/erros'
import EstadoErro from './EstadoErro.vue'

defineProps<{
  identificador: string
  titulo: string
  descricao?: string
  carregando: boolean
  erro: ErroConsulta | null
}>()

defineEmits<{ tentarNovamente: [] }>()
</script>

<template>
  <section class="secao" :aria-labelledby="identificador" :aria-busy="carregando">
    <header class="secao__cabecalho">
      <h2 :id="identificador" tabindex="-1">{{ titulo }}</h2>
      <p v-if="descricao" class="texto-apoio">{{ descricao }}</p>
      <slot name="resumo" />
    </header>
    <div v-if="carregando" aria-hidden="true">
      <slot name="carregando" />
    </div>
    <EstadoErro v-else-if="erro" :erro="erro" @tentar-novamente="$emit('tentarNovamente')" />
    <slot v-else />
  </section>
</template>

<style scoped>
.secao {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-3x);
  padding-block: var(--spacing-scale-6x);
  border-top: var(--surface-width-sm) solid var(--border);
}

.secao__cabecalho {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
}

.secao__cabecalho h2:focus {
  outline: none;
}
</style>
