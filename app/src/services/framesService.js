import api from '@/services/api'

export function fetchFrames(payload) {
    // return api.get(`frames/`)
    //           .then(response => response.data)
    return new Promise((resolve) => {
      setTimeout(() => {
        let responses = {
          data: {
            camId: payload.camId,
            fps: 20,
            frames: []
          }
        };

        let n = Math.floor(Math.random() * 300) + 101;

        for (let index=1; index <= n; index++) {
          let str = '/static/image/';
          let count = index.toString().length;
          if (count == 1) {
            str += `000${index}.jpg`
          } else if (count == 2) {
            str += `00${index}.jpg`
          } else if (count == 3) {
            str += `0${index}.jpg`
          } else {
            str += `${index}.jpg`
          }

          let response = {
            id: index,
            name: `Frame ${index}`,
            url: str,
            trackIDs: [
              {
                id: index,
                label: `Person ${index}`,
                url: str
              }
            ]
          }

          responses.data.frames.push(response)
        }

        return resolve(responses);
      }, 1500)
    });
  }
