import { fetchFrames } from '../../services/framesService'

const state = {
  frames: {
    camId: null,
    fps: 10,
    frames: []
  },
  camId: null,
}

const getters = {
  frames: state => {
    return state.frames
  },
  camId: state => state.camId
}

const actions = {
  async fetchFrames ({ commit }, payload) {
    await fetchFrames(payload)
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
    state.camId = frames.camId;
  },
  resetFrames(state) {
    state.frames = {
      camId: null,
      fps: 10,
      frames: [
        {
          id: null,
          name: null,
          url: '/static/DxnWF8.gif',
          trackIDs: []
        }
      ]
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