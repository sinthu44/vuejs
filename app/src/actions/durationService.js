import api from './api';

export function getStatus() {
  const options = {
    method: 'GET',
  };

  return api('/state', options)
    .then(response => response.data);
}

export function startRecording(payload) {
  const options = {
    method: 'POST',
    data: payload
  };

  return api('/cameras/recording/start', options)
    .then(response => response.data);
}

export function stopRecording() {
  const options = {
    method: 'POST',
  };

  return api('/cameras/recording/stop', options)
    .then(response => response.data);
}