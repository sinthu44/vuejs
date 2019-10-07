import { getStatus, startRecording, stopRecording } from "../../actions/durationService";
import { STATUS, LOADING } from "@/constants/type";

const state = {
  stateData: {
    status: STATUS.LOADING_PAGE,
    duration: 0,
    recording_time: 0,
    max_duration: 100,
  },
  loadingStart: LOADING.NO,
};

const getters = {
  stateData: state => state.stateData,
  loadingStart: state => state.loadingStart
};

const actions = {
  async fetchState({ commit }, running=null) {
    return await getStatus(running)
      .then(response => {
        commit("setStateData", response.data);
      })
  },
  async startRecording({ commit }, payload) {
    await startRecording(payload);
  },
  async stopRecording({ commit }) {
    await stopRecording();
  },
  setLoadingStart({ commit }, loadingStart) {
    commit("setLoadingStart", loadingStart);
  }
};

const mutations = {
  setStateData(state, data) {
    state.stateData = data;
  },
  setLoadingStart(state, loadingStart) {
    state.loadingStart = loadingStart;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
