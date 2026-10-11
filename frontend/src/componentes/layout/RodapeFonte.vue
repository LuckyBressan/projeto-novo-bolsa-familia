<script setup lang="ts">
import { computed } from 'vue'

import { usePeriodos } from '@/composables/usePeriodos'
import { formatarMes } from '@/dominio/formatacao'

const { periodos } = usePeriodos()

const intervalo = computed(() =>
  periodos.value
    ? `${formatarMes(periodos.value.periodo_min)} a ${formatarMes(periodos.value.periodo_max)}`
    : null,
)
</script>

<template>
  <div class="rodape">
    <div class="limite-conteudo rodape__texto texto-nota">
      <span>
        <strong class="rodape__rotulo">Fonte:</strong> Portal da Transparência (API de dados){{
          intervalo ? ` · ${intervalo}` : ''
        }}
      </span>
      <span>
        Valores conforme a última atualização da fonte, não em tempo real. Este sistema usa dados
        públicos, mas não é um site oficial do governo.
      </span>
    </div>
  </div>
</template>

<style scoped>
.rodape {
  border-top: var(--surface-width-sm) solid var(--border);
  background: var(--background-alternative);
}

.rodape__texto {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-half);
  padding-block: var(--spacing-scale-3x);
}

.rodape__rotulo {
  color: var(--color);
}
</style>
