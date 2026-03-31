import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { commentsApi } from '../api/comments';
import { projectsApi } from '../api/projects';
import { tasksApi } from '../api/tasks';
import { useAuth } from '../hooks/useAuth';
import { queryClient } from '../utils/queryClient';
import { queryKeys } from '../utils/queryKeys';
import { extractErrorMessage } from '../utils/errors';
import { Button, Card, ErrorBox, Input, Loader, Modal } from '../components/ui';
import type { Task } from '../types/api';

export const ProjectPage = () => {
  const { projectId } = useParams();
  const pid = Number(projectId);
  const [newMemberId, setNewMemberId] = useState('');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const detail = useQuery({ queryKey: queryKeys.project(pid), queryFn: () => projectsApi.detail(pid), enabled: !!pid });
  const tasks = useQuery({ queryKey: queryKeys.tasks(pid), queryFn: () => tasksApi.list(pid), enabled: !!pid });

  const addMember = useMutation({
    mutationFn: (uid: number) => projectsApi.addMember(pid, uid),
    onSuccess: async () => {
      setNewMemberId('');
      await queryClient.invalidateQueries({ queryKey: queryKeys.project(pid) });
    }
  });

  const removeMember = useMutation({
    mutationFn: (uid: number) => projectsApi.removeMember(pid, uid),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.project(pid) });
    }
  });

  const createTask = useMutation({
    mutationFn: (payload: { name: string; description: string; status: string }) => tasksApi.create(pid, payload),
    onSuccess: async () => {
      setTaskModalOpen(false);
      await queryClient.invalidateQueries({ queryKey: queryKeys.tasks(pid) });
    }
  });

  const updateTask = useMutation({
    mutationFn: ({ id, ...payload }: { id: number; name: string; description: string; status: string }) =>
      tasksApi.update(pid, id, payload),
    onSuccess: async () => {
      setEditingTask(null);
      await queryClient.invalidateQueries({ queryKey: queryKeys.tasks(pid) });
    }
  });

  const deleteTask = useMutation({
    mutationFn: (taskId: number) => tasksApi.remove(pid, taskId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.tasks(pid) });
    }
  });

  const memberIds = useMemo(() => {
    const p = detail.data as unknown as { members?: Array<{ user_id: number }>; owner_id?: number; id: number; name: string };
    return p?.members?.map((m) => m.user_id) ?? [];
  }, [detail.data]);

  if (detail.isLoading || tasks.isLoading) return <Loader label="Loading project..." />;

  return (
    <div className="space-y-6">
      <Card>
        <h1 className="text-2xl font-semibold">{detail.data?.name}</h1>
        <p className="text-sm text-slate-500">Project ID: {pid}</p>
      </Card>

      <Card className="space-y-3">
        <h2 className="text-lg font-semibold">Members</h2>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            addMember.mutate(Number(newMemberId));
          }}
        >
          <Input value={newMemberId} onChange={(e) => setNewMemberId(e.target.value)} placeholder="User ID" required />
          <Button type="submit">Add</Button>
        </form>
        <div className="flex flex-wrap gap-2">
          {memberIds.map((id) => (
            <div key={id} className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-sm">
              User #{id}
              <button
                type="button"
                className="text-red-600"
                onClick={() => {
                  if (window.confirm(`Remove user #${id}?`)) removeMember.mutate(id);
                }}
              >
                ✕
              </button>
            </div>
          ))}
          {memberIds.length === 0 && <p className="text-sm text-slate-500">No members listed.</p>}
        </div>
      </Card>

      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tasks</h2>
          <Button onClick={() => setTaskModalOpen(true)}>Create Task</Button>
        </div>

        <ErrorBox message={tasks.error ? extractErrorMessage(tasks.error) : undefined} />

        <div className="space-y-3">
          {tasks.data?.map((task) => (
            <div key={task.id} className="rounded-lg border p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-medium">{task.name}</h3>
                  <p className="text-sm text-slate-600">{task.description || 'No description'}</p>
                  <p className="mt-1 text-xs uppercase text-slate-400">{task.status || 'unknown'}</p>
                </div>
                <div className="flex gap-2">
                  <Button className="bg-amber-500 hover:bg-amber-600" onClick={() => setEditingTask(task)}>
                    Edit
                  </Button>
                  <Button
                    className="bg-red-600 hover:bg-red-700"
                    onClick={() => {
                      if (window.confirm('Delete this task?')) deleteTask.mutate(task.id);
                    }}
                  >
                    Delete
                  </Button>
                </div>
              </div>
              <button className="mt-3 text-sm text-primary-700 hover:underline" onClick={() => setSelectedTask(task)}>
                Open comments
              </button>
            </div>
          ))}
        </div>
      </Card>

      <TaskModal
        open={taskModalOpen}
        title="Create Task"
        onClose={() => setTaskModalOpen(false)}
        onSubmit={(payload) => createTask.mutate(payload)}
        loading={createTask.isPending}
      />

      <TaskModal
        open={!!editingTask}
        title="Edit Task"
        onClose={() => setEditingTask(null)}
        onSubmit={(payload) => editingTask && updateTask.mutate({ id: editingTask.id, ...payload })}
        loading={updateTask.isPending}
        initial={editingTask ?? undefined}
      />

      <CommentsModal task={selectedTask} projectId={pid} onClose={() => setSelectedTask(null)} />
    </div>
  );
};

const TaskModal = ({
  open,
  title,
  onClose,
  onSubmit,
  loading,
  initial
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  onSubmit: (payload: { name: string; description: string; status: string }) => void;
  loading: boolean;
  initial?: Task;
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('todo');

  useEffect(() => {
    setName(initial?.name || '');
    setDescription(initial?.description || '');
    setStatus(initial?.status || 'todo');
  }, [initial, open]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({ name, description, status });
  };

  return (
    <Modal open={open} onClose={onClose} title={title}>
      <form className="space-y-3" onSubmit={submit}>
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Task name" required />
        <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
        <Input value={status} onChange={(e) => setStatus(e.target.value)} placeholder="Status" required />
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </form>
    </Modal>
  );
};

const CommentsModal = ({ task, projectId, onClose }: { task: Task | null; projectId: number; onClose: () => void }) => {
  const me = useAuth();
  const [text, setText] = useState('');
  const [editing, setEditing] = useState<{ id: number; text: string } | null>(null);

  const comments = useQuery({
    queryKey: queryKeys.comments(projectId, task?.id || 0),
    queryFn: () => commentsApi.list(projectId, task!.id),
    enabled: !!task
  });

  const create = useMutation({
    mutationFn: (value: string) => commentsApi.create(projectId, task!.id, value),
    onSuccess: async () => {
      setText('');
      await queryClient.invalidateQueries({ queryKey: queryKeys.comments(projectId, task!.id) });
    }
  });

  const update = useMutation({
    mutationFn: ({ id, text: value }: { id: number; text: string }) => commentsApi.update(projectId, task!.id, id, value),
    onSuccess: async () => {
      setEditing(null);
      await queryClient.invalidateQueries({ queryKey: queryKeys.comments(projectId, task!.id) });
    }
  });

  const remove = useMutation({
    mutationFn: (commentId: number) => commentsApi.remove(projectId, task!.id, commentId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.comments(projectId, task!.id) });
    }
  });

  return (
    <Modal open={!!task} onClose={onClose} title={`Comments: ${task?.name || ''}`}>
      <form
        className="mb-4 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          create.mutate(text);
        }}
      >
        <Input value={text} onChange={(e) => setText(e.target.value)} placeholder="Write comment" required />
        <Button type="submit">Add</Button>
      </form>

      <div className="max-h-96 space-y-2 overflow-y-auto pr-1">
        {comments.isLoading && <Loader label="Loading comments..." />}
        {comments.data?.map((comment) => {
          const isMine = comment.author_id === me.data?.id;
          const isEditing = editing?.id === comment.id;

          return (
            <div key={comment.id} className="rounded-md border p-2 text-sm">
              <p className="mb-1 text-xs text-slate-400">Author #{comment.author_id}</p>
              {isEditing ? (
                <form
                  className="flex gap-2"
                  onSubmit={(e) => {
                    e.preventDefault();
                    update.mutate({ id: comment.id, text: editing.text });
                  }}
                >
                  <Input
                    value={editing.text}
                    onChange={(e) => setEditing({ id: comment.id, text: e.target.value })}
                    required
                  />
                  <Button type="submit" className="bg-amber-500 hover:bg-amber-600">
                    Save
                  </Button>
                </form>
              ) : (
                <p>{comment.text}</p>
              )}

              {isMine && !isEditing && (
                <div className="mt-2 flex gap-2">
                  <button
                    className="text-primary-700"
                    onClick={() => setEditing({ id: comment.id, text: comment.text })}
                    type="button"
                  >
                    Edit
                  </button>
                  <button
                    className="text-red-600"
                    type="button"
                    onClick={() => {
                      if (window.confirm('Delete this comment?')) remove.mutate(comment.id);
                    }}
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Modal>
  );
};
