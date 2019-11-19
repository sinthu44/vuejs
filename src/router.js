import Vue from 'vue'
import VueRouter from 'vue-router'
import HomePage from './containers/HomePage'
import Messages from '@/components/Messages'

Vue.use(VueRouter)

export default new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/messages',
      name: 'messages',
      component: Messages
    }
  ]
})
