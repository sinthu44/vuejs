import { fetchFrames } from '../../actions/framesService'

let state = {
  frames: {
    camId: null,
    fps: 10,
    frames: []
  },
}

const getters = {
  frames: state => {
    return state.frames
  },
  camId: state => state.camId
}

const actions = {
  async fetchFrames ({ commit }, payload) {
    return await fetchFrames(payload)
    .then(response => {
      commit('setFrames', response.data)
    })
  },
  async resetFrames({ commit }) {
    commit("resetFrames");
  },
}

const mutations = {
  setFrames (state, frames) {
    state.frames = frames;
  },
  resetFrames(state) {
    state.frames = {
      camId: null,
      fps: 10,
      frames: []
    };
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}