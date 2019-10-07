import api from './api';

export function fetchCameras() {
  const options = {
    method: 'GET',
  };

  return api('/cameras', options)
    .then(response => response.data);
}
