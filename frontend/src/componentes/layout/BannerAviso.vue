<script setup lang="ts">
import Message from 'primevue/message'
import { computed } from 'vue'

import { useModoMock } from '@/composables/useModoMock'

const AVISOS = {
  real: {
    severidade: 'info',
    simbolo: 'i',
    destaque: 'Projeto acadêmico (UNIDAVI), sem vínculo com o Governo Federal.',
    complemento: 'Os dados vêm da API pública do Portal da Transparência.',
  },
  mock: {
    severidade: 'warn',
    simbolo: '!',
    destaque: 'Dados fictícios (modo de demonstração).',
    complemento: 'Não use estes números para conferência.',
  },
} as const

const { modo } = useModoMock()
const aviso = computed(() => AVISOS[modo.value])
</script>

<template>
  <Message
    class="banner"
    :class="`banner--${modo}`"
    :severity="aviso.severidade"
    :closable="false"
    role="status"
  >
    <template #icon>
      <span class="banner__icone" aria-hidden="true">{{ aviso.simbolo }}</span>
    </template>
    <strong>{{ aviso.destaque }}</strong> {{ aviso.complemento }}
  </Message>
</template>

<style scoped>
.banner {
  border-radius: 0;
  outline: none;
  border-bottom: var(--surface-width-sm) solid var(--info);
}

.banner--mock {
  border-bottom-color: var(--warning);
}

.banner :deep(.p-message-content) {
  justify-content: center;
  padding: var(--spacing-scale-baseh) var(--spacing-scale-3x);
}

.banner :deep(.p-message-text) {
  flex: 0 1 auto;
}

.banner__icone {
  display: grid;
  place-items: center;
  flex: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--info);
  color: var(--on-info);
  font-size: 0.875rem;
  font-weight: 800;
  line-height: 1;
}

.banner--mock .banner__icone {
  background: var(--warning);
  color: var(--on-warning);
}

@media (max-width: 575px) {
  .banner :deep(.p-message-content) {
    align-items: flex-start;
    padding-inline: var(--spacing-scale-2x);
  }
}
</style>
