export interface User {
  id: number;
  name: string;
  email: string;
}

export interface ProjectMember {
  user_id: number;
  role: 'owner' | 'member' | string;
}

export interface Project {
  id: number;
  name: string;
  owner_id?: number;
  members?: ProjectMember[];
}

export interface Task {
  id: number;
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'done' | string;
  assignee_id: number;
  created_at?: string;
}

export interface Comment {
  id: number;
  author_id: number;
  text: string;
  created_at?: string;
}

export interface ApiError {
  detail?: string;
}