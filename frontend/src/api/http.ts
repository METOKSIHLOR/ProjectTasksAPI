import axios from 'axios';

export const http = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true
});

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401 && !window.location.pathname.startsWith('/login')) {
      window.location.assign('/login');
    }
    return Promise.reject(error);
  }
);
