import Vue from 'vue';
import App from '@/App.vue';
import "./plugins/vuetify";
import 'vuetify/dist/vuetify.min.css';
import 'ant-design-vue/dist/antd.css';
import 'vuetify/src/stylus/app.styl';
import store from '@/store' ;
import router from '@/router';
import _ from 'lodash';

export const bus = new Vue();
Vue.config.productionTip = false

const vue = new Vue({
  router,
  store,
  render: h => h(App),
  _
})

vue.$mount('#app')
