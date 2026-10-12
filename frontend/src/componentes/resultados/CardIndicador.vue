<script setup lang="ts">
import Card from 'primevue/card'

defineProps<{
  titulo: string
  valor: string
  valorCompacto: string
  complemento?: string
  compacto?: boolean
  nivel?: 3 | 4
}>()
</script>

<template>
  <Card class="indicador" :class="{ 'indicador--compacto': compacto }">
    <template #title>
      <component :is="`h${nivel ?? 4}`" class="indicador__titulo">
        <slot name="titulo">{{ titulo }}</slot>
      </component>
    </template>
    <template #content>
      <span class="indicador__valor" :title="valor">{{ compacto ? valorCompacto : valor }}</span>
      <span v-if="complemento && !compacto" class="indicador__complemento">{{ complemento }}</span>
    </template>
  </Card>
</template>

<style scoped>
.indicador {
  min-width: 0;
}

.indicador__titulo {
  display: flex;
  align-items: center;
  gap: var(--spacing-scale-base);
  color: var(--color-secondary);
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.45;
}

.indicador :deep(.p-card-content) {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
}

.indicador__valor {
  font-size: 1.815rem;
  font-weight: 700;
  line-height: 1.15;
  overflow-wrap: anywhere;
}

.indicador__complemento {
  color: var(--color-secondary);
}

.indicador--compacto :deep(.p-card-body) {
  gap: var(--spacing-scale-half);
  padding: var(--spacing-scale-baseh);
}

.indicador--compacto .indicador__valor {
  font-size: 1.26rem;
}
</style>
