import { fetchCameras } from '../../actions/camerasService'

const state = {
  cameras: []
}

const getters = {
  cameras: state => {
    return state.cameras
  },
};

const actions = {
  async fetchCameras ({ commit }) {
    return await fetchCameras ()
    .then(response => {
      commit('setCameras', response.data)
    })
  },
}

const mutations = {
  setCameras (state, data) {
    state.cameras = data.sort((a, b) => a.id - b.id);
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}