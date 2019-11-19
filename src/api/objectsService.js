export function getObjects(
  camId,
  frameId,
  trackId,
  topNum,
  reIdCams
) {
  let response = {
    data: {
      objects: [
        {
          id: 1,
          url: "/static/image/0014.jpg",
          frame_url: "/static/image/0014.jpg"
        },
        {
          id: 2,
          url: "/static/image/0015.jpg",
          frame_url: "/static/image/0015.jpg"
        },
        {
          id: 3,
          url: "/static/image/0016.jpg",
          frame_url: "/static/image/0016.jpg"
        },
        {
          id: 4,
          url: "/static/image/0017.jpg",
          frame_url: "/static/image/0017.jpg"
        }
      ]
    }
  };

  return new Promise(function(resolve) {
    resolve(response);
  });
}
