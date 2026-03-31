import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { authApi } from '../api/auth';
import { queryClient } from '../utils/queryClient';
import { queryKeys } from '../utils/queryKeys';
import { useAuth } from '../hooks/useAuth';
import { Button } from './ui';

export const AppShell = () => {
  const navigate = useNavigate();
  const me = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);

  const initials = useMemo(() => {
    const name = me.data?.name?.trim();
    if (!name) return 'U';
    return name[0].toUpperCase();
  }, [me.data?.name]);

  const logout = useMutation({
    mutationFn: authApi.logout,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.me });
      navigate('/login');
    }
  });

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="relative flex items-center gap-3">
            <button
              type="button"
              onClick={() => setProfileOpen((v) => !v)}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-sm font-bold text-white shadow-sm transition hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary-300"
              aria-label="Open profile info"
              title="Profile"
            >
              {initials}
            </button>

            <Link to="/" className="text-lg font-semibold text-primary-700">
              ProjectTasks
            </Link>

            {profileOpen && (
              <div className="absolute left-0 top-12 z-20 min-w-64 rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
                <p className="text-xs uppercase tracking-wide text-slate-400">Profile</p>
                <p className="mt-1 text-sm font-semibold text-slate-900">{me.data?.name ?? 'Неизвестный пользователь'}</p>
                <p className="mt-1 break-all text-sm text-slate-600">{me.data?.email ?? 'Email недоступен'}</p>
                <p className="mt-2 text-xs text-slate-400">ID: {me.data?.id ?? '—'}</p>
              </div>
            )}
          </div>

          <Button onClick={() => logout.mutate()} className="bg-slate-800 hover:bg-slate-900">
            Logout
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
};