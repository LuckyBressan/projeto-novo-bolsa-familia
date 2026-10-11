<script setup lang="ts">
defineProps<{ complemento: string }>()
</script>

<template>
  <div class="inicial">
    <svg width="56" height="56" viewBox="0 0 56 56" aria-hidden="true">
      <rect class="inicial__barra" x="6" y="28" width="10" height="22" rx="2" />
      <rect class="inicial__barra" x="23" y="12" width="10" height="38" rx="2" />
      <rect class="inicial__barra" x="40" y="20" width="10" height="30" rx="2" />
    </svg>
    <p class="inicial__chamada">Preencha os filtros e clique em Gerar comparativo.</p>
    <p class="inicial__complemento">{{ complemento }}</p>
  </div>
</template>

<style scoped>
.inicial {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-scale-baseh);
  padding: var(--spacing-scale-8x) var(--spacing-scale-3x);
  border: var(--surface-width-sm) dashed var(--border-control);
  border-radius: var(--surface-rounder-md);
  text-align: center;
}

.inicial__barra {
  fill: none;
  stroke: var(--border-control);
  stroke-width: 2;
}

.inicial__chamada {
  font-size: 1.05rem;
  font-weight: 600;
}

.inicial__complemento {
  color: var(--color-secondary);
}

:root.tema-escuro.alto-contraste .inicial {
  border-width: var(--surface-width-md);
}
</style>
