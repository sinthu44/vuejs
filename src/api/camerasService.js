import api from './api'

export function fetchCameras() {
    // return api.get(`camid-list`)
    //         .then(response => response.data)

    let response = {
      data: {
        cameras: [
          {
            id: 1,
            name: 'Cam 1'
          },
          {
            id: 2,
            name: 'Cam 2'
          },
          {
            id: 3,
            name: 'Cam 3'
          },
          {
            id: 4,
            name: 'Cam 4'
          },
          {
            id: 5,
            name: 'Cam 5'
          },
        ]
      }
    };

    return new Promise(function(resolve) {
      resolve(response);
    });
  }
