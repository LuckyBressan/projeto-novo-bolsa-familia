import { describe, expect, it } from 'vitest'

import { lerEscolha, listarClasses, resolverTema } from '@/dominio/tema'

describe('tema', () => {
  it('no automático segue o sistema: contraste primeiro, depois escuro, senão claro', () => {
    expect(resolverTema('automatico', { contraste: true, escuro: true })).toBe('contraste')
    expect(resolverTema('automatico', { contraste: true, escuro: false })).toBe('contraste')
    expect(resolverTema('automatico', { contraste: false, escuro: true })).toBe('escuro')
    expect(resolverTema('automatico', { contraste: false, escuro: false })).toBe('claro')
  })

  it('a escolha do usuário vence a preferência do sistema', () => {
    const sistema = { contraste: true, escuro: true }

    expect(resolverTema('claro', sistema)).toBe('claro')
    expect(resolverTema('escuro', sistema)).toBe('escuro')
    expect(resolverTema('contraste', { contraste: false, escuro: false })).toBe('contraste')
  })

  it('escolha guardada inválida ou ausente vira automático', () => {
    expect(lerEscolha('escuro')).toBe('escuro')
    expect(lerEscolha('contraste')).toBe('contraste')
    expect(lerEscolha('automatico')).toBe('automatico')
    expect(lerEscolha('roxo')).toBe('automatico')
    expect(lerEscolha(null)).toBe('automatico')
  })

  it('traduz cada tema nas classes aplicadas ao html', () => {
    expect(listarClasses('claro')).toEqual([])
    expect(listarClasses('escuro')).toEqual(['tema-escuro'])
    expect(listarClasses('contraste')).toEqual(['tema-escuro', 'alto-contraste'])
  })
})
