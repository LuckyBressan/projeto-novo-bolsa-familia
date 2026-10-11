<script setup lang="ts">
import Button from 'primevue/button'
import { computed } from 'vue'

import type { EntradaComparacao } from '@/api/tipos'
import SeloStatus from '@/componentes/estado/SeloStatus.vue'
import { useTelaEstreita } from '@/composables/useTelaEstreita'
import { montarCards } from '@/dominio/indicadores'
import type { FiltroPeriodo } from '@/dominio/periodo'
import { descreverStatus } from '@/dominio/status'
import CardIndicador from './CardIndicador.vue'
import MarcadorSerie from './MarcadorSerie.vue'

const props = defineProps<{
  entradas: EntradaComparacao[]
  periodo: FiltroPeriodo
}>()

defineEmits<{ tentarNovamente: [] }>()

const estreita = useTelaEstreita()

const cidades = computed(() =>
  props.entradas.map((entrada, posicao) => ({
    posicao,
    codigo: entrada.municipio.codigo_ibge,
    nome: `${entrada.municipio.nome} (${entrada.municipio.uf})`,
    nomeCurto: entrada.municipio.nome,
    indicadores: entrada.indicadores,
    mensagem: descreverStatus(entrada.indicadores).mensagem,
    falhou: entrada.indicadores.status_dado === 'fonte_indisponivel',
    cards: montarCards(entrada.indicadores, props.periodo),
  })),
)

const indicadores = computed(() =>
  (cidades.value[0]?.cards ?? []).map((card, posicao) => ({
    titulo: card.titulo,
    valores: cidades.value.map((cidade) => ({ cidade, card: cidade.cards[posicao] })),
  })),
)
</script>

<template>
  <div v-if="estreita" class="grupo grupo--estreito">
    <div v-for="indicador in indicadores" :key="indicador.titulo" class="grupo__indicador">
      <h3 class="grupo__nome-indicador">{{ indicador.titulo }}</h3>
      <div class="grupo__par">
        <template v-for="{ cidade, card } in indicador.valores" :key="cidade.codigo">
          <CardIndicador
            v-if="card"
            :titulo="cidade.nomeCurto"
            :valor="card.valor"
            :valor-compacto="card.valorCompacto"
            compacto
          >
            <template #titulo>
              <MarcadorSerie :posicao="cidade.posicao" :tamanho="10" />
              {{ cidade.nomeCurto }}
            </template>
          </CardIndicador>
        </template>
      </div>
    </div>
    <ul class="grupo__situacoes">
      <li v-for="cidade in cidades" :key="cidade.codigo" class="grupo__situacao">
        <span class="grupo__situacao-linha">
          <strong>{{ cidade.nomeCurto }}</strong>
          <SeloStatus :situacao="cidade.indicadores" />
        </span>
        <span v-if="cidade.mensagem" class="grupo__mensagem">{{ cidade.mensagem }}</span>
        <span v-if="cidade.falhou">
          <Button
            label="Tentar novamente"
            severity="secondary"
            variant="outlined"
            size="small"
            @click="$emit('tentarNovamente')"
          />
        </span>
      </li>
    </ul>
    <p class="texto-nota">
      Em telas estreitas, os valores aparecem na forma curta. O valor completo fica na tabela de
      dados.
    </p>
  </div>

  <div v-else class="grupo">
    <div v-for="cidade in cidades" :key="cidade.codigo" class="grupo__cidade">
      <div class="grupo__titulo">
        <MarcadorSerie :posicao="cidade.posicao" :tamanho="14" />
        <h3>{{ cidade.nome }}</h3>
        <SeloStatus :situacao="cidade.indicadores" />
      </div>
      <p v-if="cidade.mensagem" class="grupo__mensagem">
        {{ cidade.mensagem }}
        <Button
          v-if="cidade.falhou"
          label="Tentar novamente"
          variant="text"
          size="small"
          @click="$emit('tentarNovamente')"
        />
      </p>
      <CardIndicador v-for="card in cidade.cards" :key="card.titulo" v-bind="card" />
    </div>
  </div>
</template>

<style scoped>
.grupo {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-scale-3x) var(--spacing-scale-4x);
}

.grupo__cidade {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-2x);
  min-width: 0;
}

.grupo__titulo {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-baseh);
}

.grupo__mensagem {
  color: var(--color-secondary);
}

.grupo--estreito {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-2x);
}

.grupo__indicador {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
}

.grupo__nome-indicador {
  font-size: 1.05rem;
  font-weight: 700;
}

.grupo__par {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacing-scale-base);
}

.grupo__situacoes {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-base);
  margin: 0;
  padding: 0;
  list-style: none;
}

.grupo__situacao {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-scale-half);
}

.grupo__situacao-linha {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-scale-base);
}
</style>
