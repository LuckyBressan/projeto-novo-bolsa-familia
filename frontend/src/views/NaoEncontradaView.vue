<template>
  <div class="abertura-tela">
    <h1>Página não encontrada</h1>
    <p class="texto-apoio">
      O endereço não existe neste sistema.
      <RouterLink :to="{ name: 'comparacao' }">Voltar para Comparar cidades</RouterLink>
    </p>
  </div>
</template>
