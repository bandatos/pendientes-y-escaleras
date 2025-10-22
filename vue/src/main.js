import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { pinia } from './stores'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import { aliases, md } from 'vuetify/iconsets/md'

// Importar IndexedDB para inicializarlo
import './services/indexDB.js'

//Vuetify 3
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
// import { registerPlugins } from '@/plugins'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

export const config = {
  API_URL: import.meta.env.VITE_APP_API_URL,
  PASSPHRASE: import.meta.env.VITE_APP_PASSPHRASE,
  APP_NAME: import.meta.env.VITE_APP_TITLE,
  APP_VERSION: import.meta.env.VITE_APP_VERSION,
}


const vuetify = createVuetify({
  components,
  directives,
  theme: {
    themes: {
      light: {
        colors: {
          primary: '#1867C0',
          secondary: '#5CBBF6',
        },
      },
    },
  },
  icons: {
    defaultSet: 'md',
    aliases,
    sets: {
      md,
    }
  },

})



createApp(App).use(vuetify).use(pinia).mount('#app')
