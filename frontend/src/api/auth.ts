import { http } from './http';
import type { User } from '../types/api';

export const authApi = {
  register: async (payload: { name: string; email: string; password: string }) => {
    const response = await http.post<User>('/users/registration', payload);
    return response.data;
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await http.post<{ success: boolean }>('/users/auth/login', payload);
    return response.data;
  },
  logout: async () => {
    const response = await http.post<{ success: boolean }>('/users/auth/logout');
    return response.data;
  },
  me: async () => {
    const response = await http.get<User>('/users/me');
    return response.data;
  }
};
