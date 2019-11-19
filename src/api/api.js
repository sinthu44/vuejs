import axios from 'axios'
import Cookies from 'js-cookie'

export default axios.create({
  baseURL: process.env.VUE_APP_API,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})