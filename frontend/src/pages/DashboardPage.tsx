import { FormEvent, useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { projectsApi } from '../api/projects';
import { queryKeys } from '../utils/queryKeys';
import { queryClient } from '../utils/queryClient';
import { Button, Card, ErrorBox, Input, Loader, Modal } from '../components/ui';
import { extractErrorMessage } from '../utils/errors';

export const DashboardPage = () => {
  const [showCreate, setShowCreate] = useState(false);
  const [newProject, setNewProject] = useState('');
  const [error, setError] = useState<string>();

  const projects = useQuery({ queryKey: queryKeys.projects, queryFn: projectsApi.list });

  const createProject = useMutation({
    mutationFn: (name: string) => projectsApi.create(name),
    onSuccess: async () => {
      setShowCreate(false);
      setNewProject('');
      await queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    },
    onError: (err) => setError(extractErrorMessage(err))
  });

  const onCreate = (e: FormEvent) => {
    e.preventDefault();
    setError(undefined);
    createProject.mutate(newProject);
  };

  if (projects.isLoading) return <Loader label="Loading projects..." />;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Your Projects</h1>
        <Button onClick={() => setShowCreate(true)}>Create Project</Button>
      </div>

      <ErrorBox message={projects.error ? extractErrorMessage(projects.error) : undefined} />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {projects.data?.map((project) => (
          <ProjectCard key={project.id} id={project.id} name={project.name} />
        ))}
      </div>

      {projects.data?.length === 0 && <Card>No projects yet. Create your first project.</Card>}

      <Modal title="Create Project" open={showCreate} onClose={() => setShowCreate(false)}>
        <form className="space-y-4" onSubmit={onCreate}>
          <Input value={newProject} onChange={(e) => setNewProject(e.target.value)} placeholder="Project name" required />
          <ErrorBox message={error} />
          <Button disabled={createProject.isPending} type="submit">
            {createProject.isPending ? 'Creating...' : 'Create'}
          </Button>
        </form>
      </Modal>
    </div>
  );
};

const ProjectCard = ({ id, name }: { id: number; name: string }) => {
  const [editing, setEditing] = useState(false);
  const [newName, setNewName] = useState(name);

  const rename = useMutation({
    mutationFn: (nextName: string) => projectsApi.rename(id, nextName),
    onSuccess: async () => {
      setEditing(false);
      await queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    }
  });

  const remove = useMutation({
    mutationFn: () => projectsApi.remove(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.projects });
    }
  });

  return (
    <Card className="space-y-3">
      {editing ? (
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            rename.mutate(newName);
          }}
        >
          <Input value={newName} onChange={(e) => setNewName(e.target.value)} required />
          <Button type="submit" disabled={rename.isPending}>
            Save
          </Button>
        </form>
      ) : (
        <h3 className="text-lg font-medium">{name}</h3>
      )}

      <div className="flex flex-wrap gap-2">
        <Link to={`/projects/${id}`} className="rounded-md bg-primary-600 px-3 py-2 text-sm text-white hover:bg-primary-700">
          Open
        </Link>
        <Button type="button" className="bg-amber-500 hover:bg-amber-600" onClick={() => setEditing((x) => !x)}>
          {editing ? 'Cancel' : 'Rename'}
        </Button>
        <Button
          type="button"
          className="bg-red-600 hover:bg-red-700"
          onClick={() => {
            if (window.confirm('Delete this project?')) remove.mutate();
          }}
        >
          Delete
        </Button>
      </div>
    </Card>
  );
};
