import { http } from './http';
import type { Task } from '../types/api';

export const tasksApi = {
  list: async (projectId: number) => {
    const response = await http.get<Task[]>(`/projects/${projectId}/tasks`);
    return response.data;
  },
  create: async (projectId: number, payload: { name: string; description: string; status: string }) => {
    const response = await http.post<Task>(`/projects/${projectId}/tasks`, payload);
    return response.data;
  },
  update: async (projectId: number, taskId: number, payload: { name: string; description: string; status: string }) => {
    const response = await http.patch<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}`, payload);
    return response.data;
  },
  remove: async (projectId: number, taskId: number) => {
    const response = await http.delete<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}`);
    return response.data;
  }
};
