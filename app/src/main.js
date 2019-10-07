import Vue from 'vue'
import App from '@/App.vue'
import "./plugins/vuetify";
import 'vuetify/dist/vuetify.min.css'
import 'vuetify/src/stylus/app.styl'

import store from '@/store' 
import router from '@/router'
export const bus = new Vue();
Vue.config.productionTip = false

const vue = new Vue({
  router,
  store,
  render: h => h(App)
})

vue.$mount('#app')
