import Vue from 'vue'
import Router from 'vue-router'
import HomePage from './containers/HomePage'
import Messages from '@/components/Messages'

Vue.use(Router)

export default new Router({
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
