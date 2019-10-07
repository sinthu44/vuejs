import { getObjects} from "../../actions/objectsService";
const state = {
  objects: [],
};

const getters = {
  objects: state => state.objects
};

const actions = {
  async fetchObjects({ commit }, payload) {
    return await getObjects( payload)
      .then(response => {
        commit("setObjects", response.data.objects);
      })
  },
  async resetObjects({ commit }) {
    commit("resetObjects");
  },
};

const mutations = {
  setObjects(state, data) {
    state.objects = data;
  },
  resetObjects(state) {
    state.objects = [];
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
