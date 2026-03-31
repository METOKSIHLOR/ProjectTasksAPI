export const queryKeys = {
  me: ['me'] as const,
  projects: ['projects'] as const,
  project: (id: number) => ['projects', id] as const,
  tasks: (projectId: number) => ['projects', projectId, 'tasks'] as const,
  comments: (projectId: number, taskId: number) => ['projects', projectId, 'tasks', taskId, 'comments'] as const
};
