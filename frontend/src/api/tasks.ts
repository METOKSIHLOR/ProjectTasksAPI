import { http } from './http';
import type { Task } from '../types/api';

export type CreateTaskPayload = {
  title: string;
  description: string;
  assignee_id: number;
};

export type UpdateTaskPayload = {
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done';
};

export const tasksApi = {
  list: async (projectId: number) => {
    const response = await http.get<Task[]>(`/projects/${projectId}/tasks`);
    return response.data;
  },
  create: async (projectId: number, payload: CreateTaskPayload) => {
    const response = await http.post<Task>(`/projects/${projectId}/tasks`, payload);
    return response.data;
  },
  update: async (projectId: number, taskId: number, payload: UpdateTaskPayload) => {
    const response = await http.patch<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}`, payload);
    return response.data;
  },
  remove: async (projectId: number, taskId: number) => {
    const response = await http.delete<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}`);
    return response.data;
  }
};