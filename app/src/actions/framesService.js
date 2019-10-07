import api from './api';

export function fetchFrames({camId}) {
  const options = {
    method: 'GET',
  }

  return api(`/cameras/${camId}/frames`, options)
    .then(response => response.data)
}