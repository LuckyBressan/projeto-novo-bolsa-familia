<script setup lang="ts">
import type { TabelaDados } from '@/dominio/graficos'

defineProps<{
  legenda: string
  tabela: TabelaDados
}>()
</script>

<template>
  <details class="dados">
    <summary class="dados__abrir">Ver dados em tabela</summary>
    <div class="tabela-rolagem">
      <table class="tabela">
        <caption v-text="legenda" />
        <thead>
          <tr>
            <th scope="col">{{ tabela.primeira }}</th>
            <th v-for="coluna in tabela.colunas" :key="coluna" scope="col" class="tabela__numero">
              {{ coluna }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="linha in tabela.linhas" :key="linha.rotulo">
            <th scope="row">{{ linha.rotulo }}</th>
            <td v-for="(valor, posicao) in linha.valores" :key="posicao" class="tabela__numero">
              {{ valor }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </details>
</template>

<style scoped>
.dados__abrir {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-scale-base);
  min-height: var(--spacing-scale-5x);
  padding-inline: var(--spacing-scale-2x);
  border-radius: var(--surface-rounder-pill);
  color: var(--interactive);
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  list-style: none;
}

.dados__abrir::-webkit-details-marker {
  display: none;
}

.dados__abrir::before {
  content: '▸';
}

.dados[open] .dados__abrir::before {
  content: '▾';
}

.dados__abrir:hover {
  background: var(--interactive-subtle);
  color: var(--color);
}

.dados .tabela-rolagem {
  margin-top: var(--spacing-scale-2x);
}
</style>
