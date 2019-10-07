import Vue from 'vue'
import Vuex from 'vuex'
import cameras from './modules/cameras'
import objects from './modules/objects'
import frames from './modules/frames'
import duration from './modules/duration'
import reIdCams from './modules/reIdCams'
import loadingMaster from './modules/loadingMaster'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    cameras,
    objects,
    frames,
    duration,
    reIdCams,
    loadingMaster,
  }
})