import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Loader } from './ui';
import { useAuth } from '../hooks/useAuth';

export const ProtectedRoute = () => {
  const { data, isLoading, isError } = useAuth();
  const location = useLocation();

  if (isLoading) return <Loader label="Checking session..." />;
  if (isError || !data) return <Navigate to="/login" state={{ from: location.pathname }} replace />;

  return <Outlet />;
};

export const PublicOnlyRoute = () => {
  const { data, isLoading } = useAuth();

  if (isLoading) return <Loader label="Checking session..." />;
  if (data) return <Navigate to="/" replace />;

  return <Outlet />;
};
