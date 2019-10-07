const state = {
  loadingMaster: false
};

const getters = {
  loadingMaster: state => state.loadingMaster,
};

const actions = {
  setLoadingMaster({ commit }, loadingMaster) {
    commit("setLoadingMaster", loadingMaster);
  },
};

const mutations = {
  setLoadingMaster(state, loadingMaster) {
    state.loadingMaster = loadingMaster;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
