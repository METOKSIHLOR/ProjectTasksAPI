import { FormEvent, useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { commentsApi } from '../api/comments';
import { projectsApi } from '../api/projects';
import { tasksApi, type CreateTaskPayload, type UpdateTaskPayload } from '../api/tasks';
import { useAuth } from '../hooks/useAuth';
import { queryClient } from '../utils/queryClient';
import { queryKeys } from '../utils/queryKeys';
import { extractErrorMessage } from '../utils/errors';
import { Button, Card, ErrorBox, Input, Loader, Modal } from '../components/ui';
import type { Project, ProjectMember, Task } from '../types/api';

const TASK_STATUSES: Array<'todo' | 'in_progress' | 'done'> = ['todo', 'in_progress', 'done'];

export const ProjectPage = () => {
  const { projectId } = useParams();
  const pid = Number(projectId);
  const me = useAuth();
  const [newMemberId, setNewMemberId] = useState('');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const detail = useQuery({ queryKey: queryKeys.project(pid), queryFn: () => projectsApi.detail(pid), enabled: !!pid });
  const tasks = useQuery({ queryKey: queryKeys.tasks(pid), queryFn: () => tasksApi.list(pid), enabled: !!pid });

  const projectData = detail.data as Project | undefined;
  const members = useMemo(() => projectData?.members ?? [], [projectData]);
  const memberIds = useMemo(() => members.map((m) => m.user_id), [members]);

  const addMember = useMutation({
    mutationFn: (uid: number) => projectsApi.addMember(pid, uid),
    onSuccess: async (_, uid) => {
      setNewMemberId('');

      queryClient.setQueryData<Project | undefined>(queryKeys.project(pid), (prev) => {
        if (!prev) return prev;
        const exists = prev.members?.some((m) => m.user_id === uid);
        if (exists) return prev;

        return {
          ...prev,
          members: [...(prev.members ?? []), { user_id: uid, role: 'member' }]
        };
      });

      await queryClient.invalidateQueries({ queryKey: queryKeys.project(pid) });
      await detail.refetch();
    }
  });

  const removeMember = useMutation({
    mutationFn: (uid: number) => projectsApi.removeMember(pid, uid),
    onSuccess: async (_, uid) => {
      queryClient.setQueryData<Project | undefined>(queryKeys.project(pid), (prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          members: (prev.members ?? []).filter((member) => member.user_id !== uid)
        };
      });

      await queryClient.invalidateQueries({ queryKey: queryKeys.project(pid) });
      await detail.refetch();
    }
  });

  const createTask = useMutation({
    mutationFn: (payload: CreateTaskPayload) => tasksApi.create(pid, payload),
    onSuccess: async () => {
      setTaskModalOpen(false);
      await queryClient.invalidateQueries({ queryKey: queryKeys.tasks(pid) });
    }
  });

  const updateTask = useMutation({
    mutationFn: ({ id, ...payload }: { id: number } & UpdateTaskPayload) => tasksApi.update(pid, id, payload),
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

  if (detail.isLoading || tasks.isLoading) return <Loader label="Loading project..." />;

  return (
    <div className="space-y-6">
      <Card>
        <h1 className="text-2xl font-semibold">{detail.data?.name}</h1>
        <p className="text-sm text-slate-500">Project ID: {pid}</p>
      </Card>

      <Card className="space-y-4">
        <div>
          <h2 className="text-lg font-semibold">Members</h2>
          <p className="mt-1 text-sm text-slate-500">Project members: {members.length}</p>
        </div>

        <ErrorBox message={addMember.error ? extractErrorMessage(addMember.error) : undefined} />
        <ErrorBox message={removeMember.error ? extractErrorMessage(removeMember.error) : undefined} />

        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            addMember.mutate(Number(newMemberId));
          }}
        >
          <Input value={newMemberId} onChange={(e) => setNewMemberId(e.target.value)} placeholder="User ID" required />
          <Button type="submit" disabled={addMember.isPending}>
            {addMember.isPending ? 'Adding...' : 'Add'}
          </Button>
        </form>

        <div className="grid gap-3 md:grid-cols-2">
          {members.map((member) => (
            <MemberCard
              key={member.user_id}
              member={member}
              isCurrentUser={member.user_id === me.data?.id}
              onRemove={() => {
                if (window.confirm(`Remove user #${member.user_id}?`)) removeMember.mutate(member.user_id);
              }}
            />
          ))}
        </div>

        {members.length === 0 && <p className="text-sm text-slate-500">No members listed.</p>}
      </Card>

      <Card className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">Tasks</h2>
          <Button onClick={() => setTaskModalOpen(true)}>Create Task</Button>
        </div>

        <ErrorBox message={tasks.error ? extractErrorMessage(tasks.error) : undefined} />
        <ErrorBox message={createTask.error ? extractErrorMessage(createTask.error) : undefined} />
        <ErrorBox message={updateTask.error ? extractErrorMessage(updateTask.error) : undefined} />

        <div className="space-y-3">
          {tasks.data?.map((task) => (
            <div key={task.id} className="rounded-lg border p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-medium">{task.title}</h3>
                  <p className="text-sm text-slate-600">{task.description || 'No description'}</p>
                  <p className="mt-1 text-xs uppercase text-slate-400">{task.status || 'unknown'}</p>
                  <p className="mt-1 text-xs text-slate-400">Assignee #{task.assignee_id}</p>
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
          {tasks.data?.length === 0 && <p className="text-sm text-slate-500">No tasks yet.</p>}
        </div>
      </Card>

      <TaskModal
        open={taskModalOpen}
        title="Create Task"
        mode="create"
        onClose={() => setTaskModalOpen(false)}
        onCreate={(payload) => createTask.mutate(payload)}
        loading={createTask.isPending}
        memberIds={memberIds}
      />

      <TaskModal
        open={!!editingTask}
        title="Edit Task"
        mode="edit"
        onClose={() => setEditingTask(null)}
        onEdit={(payload) => editingTask && updateTask.mutate({ id: editingTask.id, ...payload })}
        loading={updateTask.isPending}
        initial={editingTask ?? undefined}
        memberIds={memberIds}
      />

      <CommentsModal task={selectedTask} projectId={pid} onClose={() => setSelectedTask(null)} />
    </div>
  );
};

const MemberCard = ({
  member,
  isCurrentUser,
  onRemove
}: {
  member: ProjectMember;
  isCurrentUser: boolean;
  onRemove: () => void;
}) => {
  const first = `U${member.user_id}`.charAt(0).toUpperCase();
  const roleText = member.role === 'owner' ? 'Owner' : 'Member';

  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-sm font-semibold text-white">
          {first}
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">User #{member.user_id}</p>
          <p className="text-xs text-slate-500">
            {roleText}
            {isCurrentUser ? ' · You' : ''}
          </p>
        </div>
      </div>

      {member.role !== 'owner' ? (
        <button type="button" className="text-sm text-red-600 hover:underline" onClick={onRemove}>
          Remove
        </button>
      ) : (
        <span className="rounded-full bg-primary-100 px-2 py-1 text-xs text-primary-700">Owner</span>
      )}
    </div>
  );
};

const TaskModal = ({
  open,
  title,
  mode,
  onClose,
  loading,
  memberIds,
  initial,
  onCreate,
  onEdit
}: {
  open: boolean;
  title: string;
  mode: 'create' | 'edit';
  onClose: () => void;
  loading: boolean;
  memberIds: number[];
  initial?: Task;
  onCreate?: (payload: CreateTaskPayload) => void;
  onEdit?: (payload: UpdateTaskPayload) => void;
}) => {
  const [taskTitle, setTaskTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<'todo' | 'in_progress' | 'done'>('todo');
  const [assigneeId, setAssigneeId] = useState('');

  useEffect(() => {
    if (mode === 'edit' && initial) {
      setTaskTitle(initial.title);
      setDescription(initial.description || '');
      setStatus((TASK_STATUSES.includes(initial.status as 'todo' | 'in_progress' | 'done')
        ? initial.status
        : 'todo') as 'todo' | 'in_progress' | 'done');
      setAssigneeId(String(initial.assignee_id ?? ''));
      return;
    }

    setTaskTitle('');
    setDescription('');
    setStatus('todo');
    setAssigneeId(memberIds[0] ? String(memberIds[0]) : '');
  }, [initial, open, mode, memberIds]);

  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (mode === 'create') {
      onCreate?.({ title: taskTitle, description, assignee_id: Number(assigneeId) });
      return;
    }

    onEdit?.({ title: taskTitle, description, status });
  };

  return (
    <Modal open={open} onClose={onClose} title={title}>
      <form className="space-y-3" onSubmit={submit}>
        <Input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} placeholder="Task title" required />
        <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" required />

        <label className="block text-sm text-slate-600">
          Status
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value as 'todo' | 'in_progress' | 'done')}
            className="mt-1 w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-900 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200"
          >
            {TASK_STATUSES.map((s) => (
              <option value={s} key={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        {mode === 'create' && (
          <label className="block text-sm text-slate-600">
            Assignee ID
            <Input
              value={assigneeId}
              onChange={(e) => setAssigneeId(e.target.value)}
              placeholder={memberIds[0] ? `Например: ${memberIds[0]}` : 'Введите user id участника проекта'}
              required
            />
          </label>
        )}

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
    <Modal open={!!task} onClose={onClose} title={`Comments: ${task?.title || ''}`}>
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