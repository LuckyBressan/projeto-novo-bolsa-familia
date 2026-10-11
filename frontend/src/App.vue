<script setup lang="ts">
import { onMounted } from 'vue'

import BannerAviso from '@/componentes/layout/BannerAviso.vue'
import CabecalhoApp from '@/componentes/layout/CabecalhoApp.vue'
import RodapeFonte from '@/componentes/layout/RodapeFonte.vue'
import { useModoMock } from '@/composables/useModoMock'
import { usePeriodos } from '@/composables/usePeriodos'

const { carregar: carregarModo } = useModoMock()
const { carregar: carregarPeriodos } = usePeriodos()

onMounted(() => {
  carregarModo()
  carregarPeriodos()
})
</script>

<template>
  <div class="app">
    <a href="#conteudo" class="app__pular">Pular para o conteúdo</a>
    <header>
      <BannerAviso />
      <CabecalhoApp />
    </header>
    <main id="conteudo" class="limite-conteudo app__conteudo" tabindex="-1">
      <RouterView />
    </main>
    <footer>
      <RodapeFonte />
    </footer>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app__pular {
  position: absolute;
  left: -9999px;
  top: var(--spacing-scale-base);
  z-index: 60;
  padding: var(--spacing-scale-base) var(--spacing-scale-2x);
  border-radius: var(--surface-rounder-sm);
  background: var(--interactive);
  color: var(--on-interactive);
  font-weight: 600;
}

.app__pular:focus {
  left: var(--spacing-scale-2x);
}

.app__conteudo {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-4x);
  padding-block: var(--spacing-scale-6x) var(--spacing-scale-3x);
}

.app__conteudo:focus {
  outline: none;
}
</style>
