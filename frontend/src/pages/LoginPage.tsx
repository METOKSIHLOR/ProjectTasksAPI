import { FormEvent, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { queryClient } from '../utils/queryClient';
import { queryKeys } from '../utils/queryKeys';
import { Button, ErrorBox, Input } from '../components/ui';
import { extractErrorMessage } from '../utils/errors';

export const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string>();

  const login = useMutation({
    mutationFn: authApi.login,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.me });
      navigate(location.state?.from || '/');
    },
    onError: (err) => setError(extractErrorMessage(err))
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError(undefined);
    login.mutate({ email, password });
  };

  return (
    <div className="mx-auto mt-24 max-w-md rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="mb-6 text-center text-2xl font-semibold">Login</h1>
      <form className="space-y-4" onSubmit={onSubmit}>
        <Input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email" required />
        <Input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" required />
        <ErrorBox message={error} />
        <Button type="submit" className="w-full" disabled={login.isPending}>
          {login.isPending ? 'Signing in...' : 'Sign in'}
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-slate-600">
        No account?{' '}
        <Link to="/register" className="text-primary-700 hover:underline">
          Register
        </Link>
      </p>
    </div>
  );
};
