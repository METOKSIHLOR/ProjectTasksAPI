import { http } from './http';
import type { Project } from '../types/api';

export const projectsApi = {
  list: async () => {
    const response = await http.get<Project[]>('/projects');
    return response.data;
  },
  create: async (name: string) => {
    const response = await http.post<Project>('/projects', { name });
    return response.data;
  },
  detail: async (projectId: number) => {
    const response = await http.get<Project>(`/projects/${projectId}`);
    return response.data;
  },
  rename: async (projectId: number, name: string) => {
    const response = await http.patch<{ success: boolean }>(`/projects/${projectId}`, { name });
    return response.data;
  },
  remove: async (projectId: number) => {
    const response = await http.delete<{ success: boolean }>(`/projects/${projectId}`);
    return response.data;
  },
  addMember: async (projectId: number, userId: number) => {
    const response = await http.post<{ success: boolean }>(`/projects/${projectId}/members`, { user_id: userId });
    return response.data;
  },
  removeMember: async (projectId: number, userId: number) => {
    const response = await http.delete<{ success: boolean }>(`/projects/${projectId}/members`, { data: { user_id: userId } });
    return response.data;
  }
};
