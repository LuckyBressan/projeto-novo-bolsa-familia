import { createRouter, createWebHistory } from 'vue-router'

const NOME_SISTEMA = 'Comparativo do Novo Bolsa Família'

declare module 'vue-router' {
  interface RouteMeta {
    titulo: string
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'comparacao',
      component: () => import('@/views/ComparacaoCidadesView.vue'),
      meta: { titulo: 'Comparar cidades' },
    },
    {
      path: '/capitais',
      name: 'capitais',
      component: () => import('@/views/CapitaisView.vue'),
      meta: { titulo: 'Capitais' },
    },
    {
      path: '/:caminho(.*)*',
      name: 'nao-encontrada',
      component: () => import('@/views/NaoEncontradaView.vue'),
      meta: { titulo: 'Página não encontrada' },
    },
  ],
})

router.afterEach((rota) => {
  document.title = `${rota.meta.titulo} · ${NOME_SISTEMA}`
})

export default router
