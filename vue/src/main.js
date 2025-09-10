import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { pinia } from './stores'

//Vuetify 3
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
    components,
    directives,
})



createApp(App).use(vuetify).use(pinia).mount('#app')
