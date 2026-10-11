<script setup lang="ts">
import ProgressSpinner from 'primevue/progressspinner'
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps<{
  mensagem: string
  mensagemDemora: string
  aposMs: number
}>()

const demorando = ref(false)
let temporizador: ReturnType<typeof setTimeout> | undefined

onMounted(() => {
  temporizador = setTimeout(() => {
    demorando.value = true
  }, props.aposMs)
})

onBeforeUnmount(() => clearTimeout(temporizador))
</script>

<template>
  <div class="carregando" role="status" aria-live="polite">
    <ProgressSpinner class="carregando__giro" stroke-width="4" aria-label="Carregando" />
    <div class="carregando__texto">
      <strong>{{ mensagem }}</strong>
      <span v-if="demorando" class="carregando__demora">{{ mensagemDemora }}</span>
    </div>
  </div>
</template>

<style scoped>
.carregando {
  display: flex;
  align-items: center;
  gap: var(--spacing-scale-2x);
}

.carregando__giro {
  flex: none;
  width: 40px;
  height: 40px;
  margin: 0;
}

.carregando__texto {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.carregando__demora {
  color: var(--color-secondary);
}
</style>
