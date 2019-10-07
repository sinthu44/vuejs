import { fetchReIDCam } from "../../services/camerasService";

const state = {
  numTop: 10,
  listChips: [],
  listReIDCams:[],
};

const getters = {
  listReIDCams: state => state.listReIDCam,
  numTop: state => state.numTop,
  listChips: state => state.listChips
};

const actions = {
  async fetchListReIDCams ({ commit }) {
    await fetchReIDCam()
    .then(response => {
      commit('setListReIDCam', response.data.reidcams)
    })
  },
  getNumTop({ commit }, data) {
    commit("setNumTop", data);
  },
  getListChipsSelect({ commit }, data) {
    commit("setListChipsSelect", data);
  }
};

const mutations = {
  setListReIDCam(state, data) {
    state.listReIDCams = data;
  },
  setNumTop(state, data) {
    state.numTop = data;
  },
  setListChipsSelect(state, data) {
    state.listChips = data;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
