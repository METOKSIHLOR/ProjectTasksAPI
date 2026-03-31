import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { authApi } from '../api/auth';
import { extractErrorMessage } from '../utils/errors';
import { Button, ErrorBox, Input } from '../components/ui';

export const RegisterPage = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string>();

  const register = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => navigate('/login'),
    onError: (err) => setError(extractErrorMessage(err))
  });

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError(undefined);
    register.mutate({ name, email, password });
  };

  return (
    <div className="mx-auto mt-24 max-w-md rounded-xl border bg-white p-6 shadow-sm">
      <h1 className="mb-6 text-center text-2xl font-semibold">Register</h1>
      <form className="space-y-4" onSubmit={onSubmit}>
        <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" required />
        <Input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="Email" required />
        <Input value={password} onChange={(e) => setPassword(e.target.value)} type="password" placeholder="Password" required />
        <ErrorBox message={error} />
        <Button type="submit" className="w-full" disabled={register.isPending}>
          {register.isPending ? 'Creating...' : 'Create account'}
        </Button>
      </form>
      <p className="mt-4 text-center text-sm text-slate-600">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-700 hover:underline">
          Login
        </Link>
      </p>
    </div>
  );
};
