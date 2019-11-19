import Vue from 'vue'
import Vuex from 'vuex'
import messages from './modules/messages'
import cameras from './modules/cameras'
import objects from './modules/objects'
import frames from './modules/frames'
import duration from './modules/duration'
import reIdCam from './modules/reIdCam'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    messages,
    cameras,
    objects,
    frames,
    duration,
    reIdCam,
  }
})