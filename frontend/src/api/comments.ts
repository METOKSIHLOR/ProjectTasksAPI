import { http } from './http';
import type { Comment } from '../types/api';

export const commentsApi = {
  list: async (projectId: number, taskId: number) => {
    const response = await http.get<Comment[]>(`/projects/${projectId}/tasks/${taskId}/comments`);
    return response.data;
  },
  create: async (projectId: number, taskId: number, text: string) => {
    const response = await http.post<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}/comments`, { text });
    return response.data;
  },
  update: async (projectId: number, taskId: number, commentId: number, text: string) => {
    const response = await http.patch<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}/comments/${commentId}`, { text });
    return response.data;
  },
  remove: async (projectId: number, taskId: number, commentId: number) => {
    const response = await http.delete<{ success: boolean }>(`/projects/${projectId}/tasks/${taskId}/comments/${commentId}`);
    return response.data;
  }
};
