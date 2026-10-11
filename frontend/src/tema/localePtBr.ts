import { defaultOptions } from 'primevue/config'

const padrao = defaultOptions.locale

export const localePtBr = {
  ...padrao,
  clear: 'Limpar',
  apply: 'Aplicar',
  accept: 'Sim',
  reject: 'Não',
  cancel: 'Cancelar',
  emptyMessage: 'Nenhuma opção disponível',
  emptyFilterMessage: 'Nenhum resultado encontrado',
  emptySearchMessage: 'Nenhum resultado encontrado',
  searchMessage: '{0} resultados disponíveis',
  selectionMessage: '{0} itens selecionados',
  emptySelectionMessage: 'Nenhum item selecionado',
  aria: {
    ...padrao?.aria,
    selectAll: 'Todos os itens selecionados',
    unselectAll: 'Nenhum item selecionado',
    close: 'Fechar',
    previous: 'Anterior',
    next: 'Próximo',
    listLabel: 'Lista de opções',
    selectRow: 'Linha selecionada',
    unselectRow: 'Linha não selecionada',
  },
}
