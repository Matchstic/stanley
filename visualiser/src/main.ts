import Vue, { CreateElement } from 'vue'

Vue.config.productionTip = false

// setup Vue instance

import App from './App.vue'

new Vue({
  render: (h: CreateElement) => h(App),
}).$mount('#app')
