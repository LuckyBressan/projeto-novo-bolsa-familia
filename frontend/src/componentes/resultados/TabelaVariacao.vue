<script setup lang="ts">
import type { LinhaVariacao } from '@/dominio/graficos'

defineProps<{ linhas: LinhaVariacao[] }>()
</script>

<template>
  <div class="variacao">
    <h3 class="variacao__titulo">Variação em relação ao mês anterior</h3>
    <div class="tabela-rolagem">
      <table class="tabela variacao__tabela">
        <thead>
          <tr>
            <th scope="col">Cidade</th>
            <th
              v-for="celula in linhas[0]?.celulas ?? []"
              :key="celula.mes"
              scope="col"
              class="tabela__numero"
            >
              {{ celula.mes }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="linha in linhas" :key="linha.nome">
            <th scope="row">{{ linha.nome }}</th>
            <td
              v-for="celula in linha.celulas"
              :key="celula.mes"
              class="tabela__numero"
              :title="celula.dica ?? undefined"
            >
              {{ celula.texto }}
              <span v-if="celula.dica" class="somente-leitor">{{ celula.dica }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <span class="texto-nota">
      ▲ aumento · ▼ redução · = sem mudança · — sem mês anterior com dados para comparar.
    </span>
  </div>
</template>

<style scoped>
.variacao {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
}

.variacao__titulo {
  font-size: 1.05rem;
  font-weight: 700;
}

.variacao__tabela {
  min-width: 480px;
}
</style>
