import { fetchCameras } from '../../api/camerasService'

const state = {
  cameras: []
}

const getters = {
  cameras: state => {
    return state.cameras
  },
};

const actions = {
  fetchCameras ({ commit }) {
    fetchCameras ()
    .then(response => {
      commit('setCameras', response.data)
    })
  },
}

const mutations = {
  setCameras (state, data) {
    state.cameras = data.cameras;
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}