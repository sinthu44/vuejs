import { getObjects} from "../../services/objectsService";
const state = {
  Objects: [],
};

const getters = {
  Objects: state => state.Objects
};

const actions = {
  async fetchObjects({ commit }, camId, frameId, trackId, topNum, reIdCams) {
    await getObjects( camId, frameId, trackId, topNum, reIdCams)
      .then(response => {
        commit("setObjects", response.data.objects);
      })
      .catch(error => {
        console.error("error", error);
      });
  }
};

const mutations = {
  setObjects(state, data) {
    state.Objects=data;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
