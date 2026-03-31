import { Link, Outlet, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { queryClient } from '../utils/queryClient';
import { queryKeys } from '../utils/queryKeys';
import { Button } from './ui';

export const AppShell = () => {
  const navigate = useNavigate();

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
          <Link to="/" className="text-lg font-semibold text-primary-700">
            ProjectTasks
          </Link>
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
