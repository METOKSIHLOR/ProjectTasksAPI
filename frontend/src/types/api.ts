export interface User {
  id: number;
  name: string;
  email: string;
}

export interface Project {
  id: number;
  name: string;
  owner_id?: number;
}

export interface Task {
  id: number;
  name: string;
  description?: string;
  status?: string;
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

