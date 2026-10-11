import { describe, expect, it } from 'vitest'

import router from '@/router'

describe('rotas', () => {
  it('troca o título da aba em cada tela, inclusive na rota desconhecida', async () => {
    await router.push('/')
    expect(document.title).toBe('Comparar cidades · Comparativo do Novo Bolsa Família')

    await router.push('/capitais?referencia=4214805')
    expect(document.title).toBe('Capitais · Comparativo do Novo Bolsa Família')

    await router.push('/nao-existe')
    expect(router.currentRoute.value.name).toBe('nao-encontrada')
    expect(document.title).toBe('Página não encontrada · Comparativo do Novo Bolsa Família')
  })
})
