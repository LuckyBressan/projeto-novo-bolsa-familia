import './tema/base.css'
import './tema/fontes.css'
import './tema/tokens.css'
import './tema/componentes.css'
import 'primeicons/primeicons.css'

import PrimeVue from 'primevue/config'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { localePtBr } from './tema/localePtBr'
import { presetGovBr } from './tema/preset'

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
  locale: localePtBr,
  theme: {
    preset: presetGovBr,
    options: {
      darkModeSelector: '.tema-escuro',
      cssLayer: { name: 'primevue', order: 'base, primevue, app' },
    },
  },
})

app.mount('#app')
