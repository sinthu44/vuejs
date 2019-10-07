const state = {
  numTop: 10,
  reIdCams: [],
  validValidate: true
};

const getters = {
  numTop: state => state.numTop,
  reIdCams: state => state.reIdCams,
  validValidate: state => state.validValidate
};

const actions = {
  setNumTop({ commit }, data) {
    commit("setNumTop", data);
  },
  setReIdCams({ commit }, data) {
    commit("setReIdCams", data);
  },
  setValidValidate({ commit }, data) {
    commit("setValidValidate", data);
  }
};

const mutations = {
  setNumTop(state, data) {
    state.numTop = data;
  },
  setReIdCams(state, data) {
    state.reIdCams = data;
  },
  setValidValidate(state, data) {
    state.validValidate = data;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
