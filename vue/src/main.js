import './assets/main.css'

import App from './App.vue'
import { createApp } from 'vue'
import { pinia } from './stores'
import 'material-design-icons-iconfont/dist/material-design-icons.css'
import { aliases, md } from 'vuetify/iconsets/md'
import { registerPlugins } from '@/plugins'
// Importar IndexedDB para inicializarlo
import './services/indexDB.js'


const app = createApp(App)
app.use(pinia)
registerPlugins(app)

app.mount('#app')
