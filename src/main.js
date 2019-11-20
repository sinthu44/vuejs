import Vue from 'vue';
import App from './App.vue';
import "./plugins/vuetify";
import 'vuetify/dist/vuetify.min.css';
import 'vuetify/src/stylus/app.styl';
import store from './reducers';
import router from './router';
import * as helpers from './helpers';

Vue.config.productionTip = false;

const plugin = {
  install () {
    Vue.router = router;
    Vue.helpers = helpers;
    Vue.prototype.$helpers = helpers;
  }
}

Vue.use(plugin)

const vue = new Vue({
  router,
  store,
  render: h => h(App)
})

vue.$mount('#app')
