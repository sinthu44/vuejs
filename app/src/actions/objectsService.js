import api from './api';

export async function getObjects({
  camId,
  frameId,
  trackId,
  topNum,
  reIdCams
}) {
  reIdCams = reIdCams.join(',');

  const options = {
    method: 'GET',
    params: {
      topNum, reIdCams
    }
  };

  return api(`/cameras/${camId}/frames/${frameId}/trackIds/${trackId}/objects`, options)
    .then(response => response.data);
}
