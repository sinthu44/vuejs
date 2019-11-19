import { getStatus, startRecording, stopRecording } from "../../api/durationService";
import { STATUS } from "@/constants/type";

const state = {
  stateData: {
    status: STATUS.NO_RECORD,
    duration: 0,
    recording_time: 0
  }
};

const getters = {
  stateData: state => state.stateData
};

const actions = {
  async fetchState({ commit }, running=null) {
    await getStatus(running)
      .then(response => {
        commit("setStateData", response.data);
      })
      .catch(error => {
        // eslint-disable-next-line no-console
        console.error("error", error);
      });
  },
  async startRecording({ commit }, payload) {
    await startRecording(payload);
  },
  async stopRecording({ commit }) {
    await stopRecording();
  }
};

const mutations = {
  setStateData(state, data) {
    state.stateData = data;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
