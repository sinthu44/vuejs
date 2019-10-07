import axios from 'axios'
import { notification } from 'ant-design-vue';
import _ from 'lodash';
import { URL_API } from '../util/.env.js'

export default function api(url, options) {
  axios.defaults.baseURL = URL_API;
  axios.defaults.headers.common['Content-Type'] = 'application/json';
  axios.defaults.headers.common['Accept'] = 'application/json';

  return new Promise((resolve, reject) => {
    axios(url, options).then(response => {
      resolve(response);
    }).catch(errors => {
      let response = errors.response;
      if (
        response &&
        response.data &&
        response.data.data &&
        response.data.data.status &&
        !_.isEmpty(response.data.data.errors)
      ) {
        let status = response.data.data.status;
        let error = response.data.data.errors.detail 
          ? response.data.data.errors.detail
          : response.data.data.errors.title;

        notification['error']({
          message: `Error ${status}`,
          description: error,
          duration: 6
        });
      }

      reject(errors);
    });
  });
}