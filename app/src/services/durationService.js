import { STATUS } from "@/constants/type";

var response = {
  data: {
    status: STATUS.READY_RECORDING,
    duration: 0,
    recording_time: 0
  }
};

export function getStatus() {
  if (response.data.status === STATUS.RECORDING) {
    response.data.recording_time += 10
  }

  if (response.data.recording_time/60 > response.data.duration) {
    response.data.status = STATUS.READY_VIEWING
    response.data.recording_time = 0;
  }

  return new Promise(function(resolve) {
    resolve(response);
  });
}

export function startRecording(payload) {
  response.data.duration = payload.duration;

  return new Promise(function(resolve) {
    setTimeout(() => {
      response.data.status = STATUS.RECORDING
      resolve();
    }, 1000);
  });
}

export function stopRecording() {
  return new Promise(function(resolve) {
    setTimeout(() => {
      response.data.status = STATUS.READY_VIEWING
      response.data.recording_time = 0;
      resolve();
    }, 1000);
  });
}