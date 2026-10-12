<script setup lang="ts">
import AlternarTema from './AlternarTema.vue'
import LogoApp from './LogoApp.vue'

const telas = [
  { nome: 'comparacao', rotulo: 'Comparar cidades' },
  { nome: 'capitais', rotulo: 'Capitais' },
]
</script>

<template>
  <div class="cabecalho">
    <div class="limite-conteudo cabecalho__linha">
      <div class="cabecalho__marca">
        <LogoApp />
        <div class="cabecalho__nome">
          <span class="cabecalho__titulo">Comparativo do Novo Bolsa Família</span>
          <span class="texto-nota">Dados públicos do Portal da Transparência</span>
        </div>
      </div>
      <div class="cabecalho__controles">
        <nav class="cabecalho__navegacao" aria-label="Principal">
          <RouterLink
            v-for="tela in telas"
            :key="tela.nome"
            :to="{ name: tela.nome }"
            class="cabecalho__link"
          >
            {{ tela.rotulo }}
          </RouterLink>
        </nav>
        <AlternarTema />
      </div>
    </div>
  </div>
</template>

<style scoped>
.cabecalho {
  background: var(--surface-card);
  border-bottom: var(--surface-width-sm) solid var(--border);
  box-shadow: var(--surface-shadow-sm);
}

.cabecalho__linha {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-scale-2x) var(--spacing-scale-4x);
  padding-block: var(--spacing-scale-2x);
}

.cabecalho__marca {
  display: flex;
  align-items: center;
  gap: var(--spacing-scale-baseh);
}

.cabecalho__nome {
  display: flex;
  flex-direction: column;
}

.cabecalho__titulo {
  font-size: 1.26rem;
  font-weight: 700;
  line-height: 1.15;
}

.cabecalho__controles {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-2x) var(--spacing-scale-3x);
}

.cabecalho__navegacao {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-scale-base);
}

.cabecalho__link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding-inline: var(--spacing-scale-2x);
  border: var(--surface-width-sm) solid var(--interactive);
  border-radius: var(--surface-rounder-pill);
  color: var(--interactive);
  font-weight: 600;
  text-decoration: none;
}

.cabecalho__link:hover {
  background: var(--interactive-subtle);
  color: var(--color);
}

.cabecalho__link[aria-current='page'] {
  background: var(--interactive);
  color: var(--on-interactive);
}

:root.tema-escuro.alto-contraste .cabecalho__link {
  border-width: var(--surface-width-md);
}

@media (max-width: 575px) {
  .cabecalho__controles,
  .cabecalho__navegacao {
    width: 100%;
  }

  .cabecalho__controles > :deep(.tema) {
    width: 100%;
  }

  .cabecalho__link {
    flex: 1;
  }
}
</style>
